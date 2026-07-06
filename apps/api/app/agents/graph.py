"""LangGraph state machine for AI lead scoring.

This module implements the LangGraph StateGraph with nodes for:
- prepare_context: Gather and format lead data
- redact_pii: Remove sensitive information before LLM processing
- score_lead: Call LLM to generate scores
- validate_output: Run anti-hallucination validation
- calculate_composite: Compute weighted composite score
"""

from typing import Any, TypedDict

import structlog
from langgraph.graph import END, StateGraph

from app.agents.prompts import SYSTEM_PROMPT, build_user_prompt
from app.agents.schemas import LeadScoreResult
from app.agents.validator import AntiHallucinationValidator
from app.config import settings

logger = structlog.get_logger(__name__)


# --- Scoring providers -----------------------------------------------------
# The mock provider generates grounded, deterministic scores directly from the
# lead's real fields (so every cited_evidence item can be verified by the
# anti-hallucination validator), letting the whole pipeline run with no API
# key. The OpenAI provider is used when LLM_PROVIDER=openai and a key is set.


def _pick_evidence(*candidates: Any) -> list[str]:
    """Return grounded, non-empty string evidence drawn from real lead data."""
    evidence: list[str] = []
    for candidate in candidates:
        if candidate is None:
            continue
        text = str(candidate).strip()
        if text and text.lower() not in {"n/a", "none", ""}:
            evidence.append(text)
    return evidence or ["No supporting data found in lead record"]


def _seniority_score(job_title: str | None) -> int:
    title = (job_title or "").lower()
    if any(k in title for k in ("chief", "ceo", "cto", "cfo", "coo", "founder", "president", "owner")):
        return 10
    if "vp" in title or "vice president" in title or "head of" in title:
        return 8
    if "director" in title:
        return 7
    if "manager" in title or "lead" in title:
        return 5
    return 3 if title else 2


def _size_score(employee_count: int | None) -> int:
    if not employee_count:
        return 4
    if employee_count >= 1000:
        return 9
    if employee_count >= 250:
        return 8
    if employee_count >= 50:
        return 6
    return 4


def _timing_score(funding: dict | None) -> int:
    if not funding:
        return 4
    year = str(funding.get("date", ""))[:4]
    return 9 if year in {"2024", "2025", "2026"} else 6


def _clamp(value: int) -> int:
    return max(1, min(10, value))


def _mock_score(lead_data: dict[str, Any], criteria_configs: list[dict[str, Any]]) -> dict[str, Any]:
    """Produce grounded, deterministic criteria scores from real lead fields."""
    industry = lead_data.get("industry")
    company = lead_data.get("company") or lead_data.get("company_name")
    job_title = lead_data.get("job_title")
    employees = lead_data.get("employee_count")
    tech_stack = lead_data.get("tech_stack") or []
    funding = lead_data.get("recent_funding") or {}
    source = lead_data.get("source")

    heuristics: dict[str, tuple[int, list[str], str]] = {
        "icp_fit": (
            _size_score(employees),
            _pick_evidence(industry, company, f"{employees} employees" if employees else None),
            "Company size and industry indicate strong ICP alignment.",
        ),
        "buying_intent": (
            _clamp(6 if source else 4),
            _pick_evidence(source, *(tech_stack[:1] if tech_stack else [])),
            "Inbound source and technographic signals suggest active evaluation.",
        ),
        "authority": (
            _seniority_score(job_title),
            _pick_evidence(job_title),
            "The contact's title reflects their level of decision-making authority.",
        ),
        "pain_need": (
            _clamp(7 if tech_stack else 5),
            _pick_evidence(*(tech_stack[:2] if tech_stack else []), industry),
            "The current tech stack and industry point to a solvable pain point.",
        ),
        "timing": (
            _timing_score(funding),
            _pick_evidence(funding.get("round"), funding.get("date")),
            "Recent funding activity is a compelling event that improves timing.",
        ),
    }

    criteria_scores = []
    for cfg in criteria_configs:
        name = cfg["name"]
        score, evidence, reason = heuristics.get(
            name,
            (6, _pick_evidence(company, industry), "General fit based on available firmographic data."),
        )
        grounded = "No supporting" not in evidence[0]
        criteria_scores.append(
            {
                "criteria_name": name,
                "score": score,
                "reasoning": reason,
                "cited_evidence": evidence,
                "confidence": 0.75 if grounded else 0.4,
            }
        )

    label = company or "This lead"
    return {
        "lead_email_hash": lead_data.get("email_hash", "unknown"),
        "criteria_scores": criteria_scores,
        "overall_summary": (
            f"{label} shows a mixed but actionable profile across the five criteria, "
            f"with clear signals on fit, authority, and timing."
        ),
        "suggested_action": "Schedule a discovery call to confirm fit and current priorities.",
        "disqualify": False,
        "disqualify_reason": None,
    }


def _score_with_openai(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    """Score a lead using OpenAI structured outputs (requires OPENAI_API_KEY)."""
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0.1,
        api_key=settings.OPENAI_API_KEY,
    )
    structured = llm.with_structured_output(LeadScoreResult)
    result = structured.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    return result.model_dump()


class AgentState(TypedDict):
    """State container for the lead scoring agent."""

    lead_data: dict[str, Any]
    criteria_configs: list[dict[str, Any]]
    llm_response: dict[str, Any] | None
    validation_result: dict[str, Any] | None
    composite_score: float | None
    final_result: LeadScoreResult | None
    error: str | None


def prepare_context(state: AgentState) -> AgentState:
    """Prepare context by gathering lead data and criteria configurations.

    This node ensures all required data is present and properly formatted
    before passing to downstream nodes.

    Args:
        state: Current agent state.

    Returns:
        Updated state with validated context.
    """
    lead_data = state.get("lead_data")
    criteria_configs = state.get("criteria_configs")

    if not lead_data:
        logger.error("No lead data provided to prepare_context")
        return {**state, "error": "Missing lead data"}

    if not criteria_configs:
        logger.error("No criteria configs provided to prepare_context")
        return {**state, "error": "Missing criteria configurations"}

    # Ensure we have active criteria only
    active_criteria = [c for c in criteria_configs if c.get("is_active", True)]

    if len(active_criteria) != 5:
        logger.warning(
            "Expected 5 active criteria",
            actual_count=len(active_criteria),
        )

    logger.info(
        "Context prepared successfully",
        lead_email_hash=lead_data.get("email_hash"),
        criteria_count=len(active_criteria),
    )

    return {**state, "criteria_configs": active_criteria}


def redact_pii(state: AgentState) -> AgentState:
    """Redact personally identifiable information from lead data.

    This node creates a sanitized copy of the lead data for LLM processing,
    removing or masking sensitive fields while preserving scoring-relevant info.

    Args:
        state: Current agent state.

    Returns:
        Updated state with redacted lead data.
    """
    lead_data = state.get("lead_data", {})

    # Create a copy to avoid mutating original
    redacted_data = lead_data.copy()

    # Remove direct PII fields that shouldn't be sent to LLM
    pii_fields_to_remove = ["email", "phone", "personal_notes"]
    for field in pii_fields_to_remove:
        if field in redacted_data:
            del redacted_data[field]

    # Keep email_hash for identification but remove raw email
    # The LLM only needs the hash to include in its response

    logger.info(
        "PII redaction completed",
        fields_removed=[f for f in pii_fields_to_remove if f in lead_data],
    )

    return {**state, "lead_data": redacted_data}


def score_lead(state: AgentState) -> AgentState:
    """Call LLM to generate lead scores.

    This node constructs prompts and calls the LLM API to score the lead
    based on the configured criteria. In production, this would use LangChain
    with OpenAI or another provider. For now, it returns a mock response.

    Args:
        state: Current agent state.

    Returns:
        Updated state with LLM response.
    """
    lead_data = state.get("lead_data", {})
    criteria_configs = state.get("criteria_configs", [])

    if state.get("error"):
        return state

    try:
        # Build prompts
        system_prompt = SYSTEM_PROMPT
        user_prompt = build_user_prompt(lead_data, criteria_configs)

        logger.info(
            "LLM scoring initiated",
            prompt_length=len(system_prompt) + len(user_prompt),
        )

        # Dispatch to the configured scoring provider.
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            response = _score_with_openai(system_prompt, user_prompt)
            provider = "openai"
        else:
            response = _mock_score(lead_data, criteria_configs)
            provider = "mock"

        logger.info("Scoring provider used", provider=provider)

        # Validate against the strict Pydantic schema.
        parsed_result = LeadScoreResult.model_validate(response)

        logger.info(
            "LLM scoring completed",
            lead_email_hash=parsed_result.lead_email_hash,
            disqualify=parsed_result.disqualify,
        )

        return {**state, "llm_response": parsed_result.model_dump()}

    except Exception as e:
        logger.exception("LLM scoring failed", error=str(e))
        return {**state, "error": f"LLM scoring failed: {str(e)}"}


def validate_output(state: AgentState) -> AgentState:
    """Validate LLM output using anti-hallucination checks.

    This node runs comprehensive validation on the LLM's output to ensure:
    - All cited evidence exists in the source data
    - Criteria names match expected values
    - Scores are within valid ranges
    - Reasoning meets length constraints

    Args:
        state: Current agent state.

    Returns:
        Updated state with validation results.
    """
    if state.get("error"):
        return state

    llm_response = state.get("llm_response")
    lead_data = state.get("lead_data", {})
    criteria_configs = state.get("criteria_configs", [])

    if not llm_response:
        logger.error("No LLM response to validate")
        return {**state, "error": "No LLM response to validate"}

    expected_criteria = [c["name"] for c in criteria_configs]
    validator = AntiHallucinationValidator(
        expected_criteria=expected_criteria,
        evidence_threshold=0.85,
    )

    validation_result = validator.validate(llm_response, lead_data)

    logger.info(
        "Validation completed",
        is_valid=validation_result["is_valid"],
        total_checks=validation_result["total_checks"],
        failed_checks=validation_result["failed_checks"],
    )

    if not validation_result["is_valid"]:
        logger.warning(
            "Validation failed - may need retry or manual review",
            failed_checks=validation_result["failed_checks"],
        )
        # Note: We don't set error here to allow the graph to continue
        # The caller can decide whether to accept or reject based on validation

    return {**state, "validation_result": validation_result}


def calculate_composite(state: AgentState) -> AgentState:
    """Calculate weighted composite score from individual criteria scores.

    This node computes the final composite score using configured weights
    and determines the suggested action based on score thresholds.

    Args:
        state: Current agent state.

    Returns:
        Updated state with composite score and final result.
    """
    if state.get("error"):
        return state

    llm_response = state.get("llm_response")
    criteria_configs = state.get("criteria_configs", [])

    if not llm_response:
        return state

    criteria_scores = llm_response.get("criteria_scores", [])

    # Build weight lookup
    weight_map = {c["name"]: c["weight"] for c in criteria_configs}

    # Calculate weighted composite score
    weighted_sum = 0.0
    total_weight = 0.0

    for score in criteria_scores:
        criteria_name = score.get("criteria_name")
        score_value = score.get("score", 0)
        weight = weight_map.get(criteria_name, 0.2)  # Default equal weight

        weighted_sum += score_value * weight
        total_weight += weight

    # Normalize to 0-100 scale (individual scores are 1-10)
    composite_score = (weighted_sum / total_weight) * 10 if total_weight > 0 else 0

    # Update disqualify flag based on composite score
    should_disqualify = composite_score < 40
    
    # Update the llm_response with calculated composite
    llm_response["composite_score"] = composite_score
    if should_disqualify and not llm_response.get("disqualify"):
        llm_response["disqualify"] = True
        llm_response["disqualify_reason"] = llm_response.get("disqualify_reason") or \
            f"Composite score {composite_score:.1f} below threshold of 40"

    logger.info(
        "Composite score calculated",
        composite_score=composite_score,
        should_disqualify=should_disqualify,
    )

    # Parse final result
    try:
        final_result = LeadScoreResult.model_validate(llm_response)
        return {
            **state,
            "composite_score": composite_score,
            "final_result": final_result,
        }
    except Exception as e:
        logger.exception("Failed to parse final result", error=str(e))
        return {**state, "error": f"Failed to parse final result: {str(e)}"}


def build_scoring_graph() -> StateGraph:
    """Build and compile the LangGraph state machine for lead scoring.

    Returns:
        Compiled StateGraph ready for execution.
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("prepare_context", prepare_context)
    workflow.add_node("redact_pii", redact_pii)
    workflow.add_node("score_lead", score_lead)
    workflow.add_node("validate_output", validate_output)
    workflow.add_node("calculate_composite", calculate_composite)

    # Define edges
    workflow.set_entry_point("prepare_context")
    workflow.add_edge("prepare_context", "redact_pii")
    workflow.add_edge("redact_pii", "score_lead")
    workflow.add_edge("score_lead", "validate_output")
    workflow.add_edge("validate_output", "calculate_composite")
    workflow.add_edge("calculate_composite", END)

    logger.info("Lead scoring graph built successfully")

    return workflow.compile()


# Compiled graph instance for reuse
scoring_graph = build_scoring_graph()


async def score_lead_async(
    lead_data: dict[str, Any],
    criteria_configs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Execute the lead scoring graph asynchronously.

    Args:
        lead_data: Dictionary containing enriched lead information.
        criteria_configs: List of criteria configurations with weights.

    Returns:
        Dictionary containing scoring results or error information.
    """
    initial_state: AgentState = {
        "lead_data": lead_data,
        "criteria_configs": criteria_configs,
        "llm_response": None,
        "validation_result": None,
        "composite_score": None,
        "final_result": None,
        "error": None,
    }

    try:
        result = await scoring_graph.ainvoke(initial_state)
        
        if result.get("error"):
            return {"success": False, "error": result["error"]}
        
        return {
            "success": True,
            "result": result.get("final_result"),
            "composite_score": result.get("composite_score"),
            "validation": result.get("validation_result"),
        }
    except Exception as e:
        logger.exception("Graph execution failed", error=str(e))
        return {"success": False, "error": str(e)}
