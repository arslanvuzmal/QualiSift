"""LangGraph state machine for AI lead scoring.

This module implements the LangGraph StateGraph with nodes for:
- prepare_context: Gather and format lead data
- redact_pii: Remove sensitive information before LLM processing
- score_lead: Call LLM to generate scores
- validate_output: Run anti-hallucination validation
- calculate_composite: Compute weighted composite score
"""

from typing import Annotated, Any, TypedDict

import structlog
from langgraph.graph import END, StateGraph

from app.agents.prompts import SYSTEM_PROMPT, build_user_prompt
from app.agents.schemas import LeadScoreResult
from app.agents.validator import AntiHallucinationValidator

logger = structlog.get_logger(__name__)


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

        # TODO: Replace with actual LangChain/OpenAI call
        # Example:
        # from langchain_openai import ChatOpenAI
        # from langchain_core.output_parsers import PydanticOutputParser
        # 
        # llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        # parser = PydanticOutputParser(pydantic_object=LeadScoreResult)
        # chain = llm | parser
        # result = chain.invoke({"system": system_prompt, "user": user_prompt})
        
        # Mock response for testing (will be replaced by real LLM call)
        mock_response = {
            "lead_email_hash": lead_data.get("email_hash", "unknown"),
            "criteria_scores": [
                {
                    "criteria_name": cfg["name"],
                    "score": 7,
                    "reasoning": "Mock reasoning for testing purposes. This would contain actual analysis.",
                    "cited_evidence": ["Mock evidence from lead data"],
                    "confidence": 0.8,
                }
                for cfg in criteria_configs
            ],
            "overall_summary": "Mock summary: This lead shows moderate potential across most criteria.",
            "suggested_action": "Schedule a discovery call to discuss their current challenges.",
            "disqualify": False,
            "disqualify_reason": None,
        }

        # Validate against Pydantic schema
        parsed_result = LeadScoreResult.model_validate(mock_response)

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
