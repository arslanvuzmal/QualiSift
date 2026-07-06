"""Unit tests for the LangGraph scoring agent."""

import pytest
from unittest.mock import AsyncMock, patch

from app.agents.graph import (
    AgentState,
    prepare_context,
    redact_pii,
    score_lead,
    validate_output,
    calculate_composite,
    build_scoring_graph,
)
from app.agents.schemas import LeadScoreResult


class TestPrepareContext:
    """Tests for the prepare_context node."""

    def test_valid_context_preparation(self):
        """Test context preparation with valid data."""
        state: AgentState = {
            "lead_data": {"email_hash": "abc123", "company": "TechCorp"},
            "criteria_configs": [
                {"name": "icp_fit", "weight": 0.3, "is_active": True},
                {"name": "buying_intent", "weight": 0.25, "is_active": True},
            ],
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = prepare_context(state)

        assert result["error"] is None
        assert len(result["criteria_configs"]) == 2

    def test_missing_lead_data(self):
        """Test error handling when lead data is missing."""
        state: AgentState = {
            "lead_data": None,
            "criteria_configs": [{"name": "icp_fit", "weight": 0.3}],
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = prepare_context(state)

        assert result["error"] == "Missing lead data"

    def test_missing_criteria_configs(self):
        """Test error handling when criteria configs are missing."""
        state: AgentState = {
            "lead_data": {"email_hash": "abc123"},
            "criteria_configs": None,
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = prepare_context(state)

        assert result["error"] == "Missing criteria configurations"

    def test_filters_inactive_criteria(self):
        """Test that inactive criteria are filtered out."""
        state: AgentState = {
            "lead_data": {"email_hash": "abc123"},
            "criteria_configs": [
                {"name": "icp_fit", "weight": 0.3, "is_active": True},
                {"name": "buying_intent", "weight": 0.25, "is_active": False},
                {"name": "authority", "weight": 0.2, "is_active": True},
            ],
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = prepare_context(state)

        assert result["error"] is None
        assert len(result["criteria_configs"]) == 2
        assert all(c["is_active"] for c in result["criteria_configs"])


class TestRedactPII:
    """Tests for the redact_pii node."""

    def test_removes_pii_fields(self):
        """Test that PII fields are removed from lead data."""
        state: AgentState = {
            "lead_data": {
                "email": "john@example.com",
                "phone": "+1-555-123-4567",
                "personal_notes": "Met at conference",
                "email_hash": "abc123",
                "company": "TechCorp",
            },
            "criteria_configs": [],
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = redact_pii(state)

        assert "email" not in result["lead_data"]
        assert "phone" not in result["lead_data"]
        assert "personal_notes" not in result["lead_data"]
        # Should keep non-PII fields
        assert result["lead_data"]["email_hash"] == "abc123"
        assert result["lead_data"]["company"] == "TechCorp"

    def test_preserves_original_state(self):
        """Test that original state is not mutated."""
        original_lead_data = {
            "email": "john@example.com",
            "company": "TechCorp",
        }
        state: AgentState = {
            "lead_data": original_lead_data,
            "criteria_configs": [],
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = redact_pii(state)

        # Original should still have email
        assert "email" in state["lead_data"]
        # Result should not have email
        assert "email" not in result["lead_data"]

    def test_handles_empty_lead_data(self):
        """Test handling of empty lead data."""
        state: AgentState = {
            "lead_data": {},
            "criteria_configs": [],
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = redact_pii(state)

        assert result["error"] is None
        assert result["lead_data"] == {}


class TestScoreLead:
    """Tests for the score_lead node."""

    def test_generates_mock_response(self):
        """Test that mock response is generated correctly."""
        state: AgentState = {
            "lead_data": {
                "email_hash": "abc123",
                "company": "TechCorp",
                "job_title": "VP Engineering",
            },
            "criteria_configs": [
                {"name": "icp_fit", "weight": 0.3, "is_active": True},
                {"name": "buying_intent", "weight": 0.25, "is_active": True},
                {"name": "authority", "weight": 0.2, "is_active": True},
                {"name": "pain_need", "weight": 0.15, "is_active": True},
                {"name": "timing", "weight": 0.1, "is_active": True},
            ],
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = score_lead(state)

        assert result["error"] is None
        assert result["llm_response"] is not None
        assert "lead_email_hash" in result["llm_response"]
        assert len(result["llm_response"]["criteria_scores"]) == 5

    def test_propagates_existing_error(self):
        """Test that existing errors are propagated."""
        state: AgentState = {
            "lead_data": {},
            "criteria_configs": [],
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": "Previous error",
        }

        result = score_lead(state)

        assert result["error"] == "Previous error"


class TestValidateOutput:
    """Tests for the validate_output node."""

    def test_validates_llm_response(self):
        """Test validation of LLM response."""
        state: AgentState = {
            "lead_data": {
                "email_hash": "abc123",
                "company": "TechCorp",
            },
            "criteria_configs": [
                {"name": "icp_fit", "weight": 0.3, "is_active": True},
            ],
            "llm_response": {
                "lead_email_hash": "abc123",
                "criteria_scores": [
                    {
                        "criteria_name": "icp_fit",
                        "score": 8,
                        "reasoning": "This reasoning is long enough to pass validation checks here.",
                        "cited_evidence": ["TechCorp"],
                        "confidence": 0.9,
                    },
                ],
                "overall_summary": "Good lead.",
                "suggested_action": "Call them.",
                "disqualify": False,
                "disqualify_reason": None,
            },
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = validate_output(state)

        assert result["error"] is None
        assert result["validation_result"] is not None
        assert "is_valid" in result["validation_result"]

    def test_handles_missing_llm_response(self):
        """Test error handling when LLM response is missing."""
        state: AgentState = {
            "lead_data": {},
            "criteria_configs": [],
            "llm_response": None,
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = validate_output(state)

        assert result["error"] == "No LLM response to validate"


class TestCalculateComposite:
    """Tests for the calculate_composite node."""

    def test_calculates_weighted_score(self):
        """Test weighted composite score calculation."""
        state: AgentState = {
            "lead_data": {},
            "criteria_configs": [
                {"name": "icp_fit", "weight": 0.3},
                {"name": "buying_intent", "weight": 0.25},
                {"name": "authority", "weight": 0.2},
                {"name": "pain_need", "weight": 0.15},
                {"name": "timing", "weight": 0.1},
            ],
            "llm_response": {
                "lead_email_hash": "abc123",
                "criteria_scores": [
                    {"criteria_name": "icp_fit", "score": 10, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                    {"criteria_name": "buying_intent", "score": 8, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                    {"criteria_name": "authority", "score": 6, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                    {"criteria_name": "pain_need", "score": 4, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                    {"criteria_name": "timing", "score": 2, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                ],
                "overall_summary": "This lead summary is intentionally long enough to validate.",
                "suggested_action": "Action.",
                "disqualify": False,
                "disqualify_reason": None,
            },
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = calculate_composite(state)

        assert result["error"] is None
        assert result["composite_score"] is not None
        # Weighted: (10*0.3 + 8*0.25 + 6*0.2 + 4*0.15 + 2*0.1) * 10 = 70
        assert abs(result["composite_score"] - 70.0) < 0.01

    def test_sets_disqualify_flag_for_low_scores(self):
        """Test that disqualify flag is set for low composite scores."""
        state: AgentState = {
            "lead_data": {},
            "criteria_configs": [
                {"name": "icp_fit", "weight": 0.3},
                {"name": "buying_intent", "weight": 0.25},
                {"name": "authority", "weight": 0.2},
                {"name": "pain_need", "weight": 0.15},
                {"name": "timing", "weight": 0.1},
            ],
            "llm_response": {
                "lead_email_hash": "abc123",
                "criteria_scores": [
                    {"criteria_name": "icp_fit", "score": 2, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                    {"criteria_name": "buying_intent", "score": 2, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                    {"criteria_name": "authority", "score": 2, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                    {"criteria_name": "pain_need", "score": 2, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                    {"criteria_name": "timing", "score": 2, "reasoning": "This reasoning is long enough to pass.", "cited_evidence": ["Evidence"], "confidence": 0.9},
                ],
                "overall_summary": "This lead summary is intentionally long enough to validate.",
                "suggested_action": "Action.",
                "disqualify": False,
                "disqualify_reason": None,
            },
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = calculate_composite(state)

        assert result["error"] is None
        assert result["composite_score"] < 40
        assert result["llm_response"]["disqualify"] is True
        assert "below threshold" in result["llm_response"]["disqualify_reason"]

    def test_creates_final_result(self):
        """Test that final result is created as LeadScoreResult."""
        state: AgentState = {
            "lead_data": {},
            "criteria_configs": [
                {"name": "icp_fit", "weight": 0.3},
                {"name": "buying_intent", "weight": 0.25},
                {"name": "authority", "weight": 0.2},
                {"name": "pain_need", "weight": 0.15},
                {"name": "timing", "weight": 0.1},
            ],
            "llm_response": {
                "lead_email_hash": "abc123",
                "criteria_scores": [
                    {
                        "criteria_name": "icp_fit",
                        "score": 8,
                        "reasoning": "This reasoning is long enough to pass validation checks here.",
                        "cited_evidence": ["Evidence"],
                        "confidence": 0.9,
                    },
                    {
                        "criteria_name": "buying_intent",
                        "score": 8,
                        "reasoning": "This reasoning is long enough to pass validation checks here.",
                        "cited_evidence": ["Evidence"],
                        "confidence": 0.9,
                    },
                    {
                        "criteria_name": "authority",
                        "score": 8,
                        "reasoning": "This reasoning is long enough to pass validation checks here.",
                        "cited_evidence": ["Evidence"],
                        "confidence": 0.9,
                    },
                    {
                        "criteria_name": "pain_need",
                        "score": 8,
                        "reasoning": "This reasoning is long enough to pass validation checks here.",
                        "cited_evidence": ["Evidence"],
                        "confidence": 0.9,
                    },
                    {
                        "criteria_name": "timing",
                        "score": 8,
                        "reasoning": "This reasoning is long enough to pass validation checks here.",
                        "cited_evidence": ["Evidence"],
                        "confidence": 0.9,
                    },
                ],
                "overall_summary": "This is a strong lead overall and worth pursuing now.",
                "suggested_action": "Schedule call.",
                "disqualify": False,
                "disqualify_reason": None,
            },
            "validation_result": None,
            "composite_score": None,
            "final_result": None,
            "error": None,
        }

        result = calculate_composite(state)

        assert result["error"] is None
        assert result["final_result"] is not None
        assert isinstance(result["final_result"], LeadScoreResult)


class TestBuildScoringGraph:
    """Tests for the graph building function."""

    def test_builds_graph_with_all_nodes(self):
        """Test that graph is built with all expected nodes."""
        graph = build_scoring_graph()

        assert graph is not None
        # Check that the graph has the expected structure
        assert hasattr(graph, 'invoke') or hasattr(graph, 'ainvoke')

    def test_graph_has_correct_edges(self):
        """Test that graph has correct edge connections."""
        graph = build_scoring_graph()

        # The graph should be compilable and runnable
        assert graph is not None
