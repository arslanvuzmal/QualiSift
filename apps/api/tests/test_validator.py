"""Unit tests for the anti-hallucination validator."""

import pytest

from app.agents.validator import (
    AntiHallucinationValidator,
    calculate_similarity,
    normalize_text,
    validate_criteria_names,
    validate_score_ranges,
    verify_evidence_in_data,
)


class TestNormalizeText:
    """Tests for the normalize_text utility function."""

    def test_lowercase_conversion(self):
        """Test that text is converted to lowercase."""
        assert normalize_text("Hello WORLD") == "hello world"

    def test_whitespace_normalization(self):
        """Test that extra whitespace is removed."""
        assert normalize_text("  multiple   spaces  ") == "multiple spaces"

    def test_combined_normalization(self):
        """Test combined lowercase and whitespace normalization."""
        assert normalize_text("  HELLO   World  ") == "hello world"

    def test_empty_string(self):
        """Test handling of empty string."""
        assert normalize_text("") == ""


class TestCalculateSimilarity:
    """Tests for the calculate_similarity utility function."""

    def test_exact_match(self):
        """Test that identical strings return similarity of 1.0."""
        assert calculate_similarity("hello world", "hello world") == 1.0

    def test_completely_different(self):
        """Test that completely different strings return low similarity."""
        similarity = calculate_similarity("abc", "xyz")
        assert 0.0 <= similarity < 0.5

    def test_partial_match(self):
        """Test that partially similar strings return intermediate similarity."""
        similarity = calculate_similarity("hello world", "hello there")
        assert 0.5 < similarity < 1.0

    def test_case_insensitive(self):
        """Test that similarity calculation is case-insensitive."""
        sim1 = calculate_similarity("Hello World", "hello world")
        sim2 = calculate_similarity("HELLO WORLD", "hello world")
        assert sim1 == 1.0
        assert sim2 == 1.0

    def test_whitespace_ignored(self):
        """Test that whitespace differences don't affect similarity."""
        sim = calculate_similarity("  hello  world  ", "hello world")
        assert sim == 1.0


class TestVerifyEvidenceInData:
    """Tests for the verify_evidence_in_data function."""

    def test_exact_evidence_match(self):
        """Test verification with exact evidence match."""
        lead_data = {
            "company": "Acme Corp",
            "industry": "Technology",
            "employee_count": 500,
        }
        evidence = ["Acme Corp", "Technology"]
        results = verify_evidence_in_data(evidence, lead_data)

        assert len(results) == 2
        assert all(r["valid"] for r in results)
        assert all(r["similarity"] == 1.0 for r in results)

    def test_evidence_not_found(self):
        """Test verification when evidence is not in data."""
        lead_data = {
            "company": "Acme Corp",
            "industry": "Technology",
        }
        evidence = ["Google", "Finance"]
        results = verify_evidence_in_data(evidence, lead_data, threshold=0.85)

        assert len(results) == 2
        assert all(not r["valid"] for r in results)

    def test_nested_dict_evidence(self):
        """Test verification with nested dictionary data."""
        lead_data = {
            "company": "TechStart",
            "funding": {
                "round": "Series B",
                "amount": 50000000,
                "investor": "Sequoia Capital",
            },
        }
        evidence = ["Series B", "Sequoia Capital"]
        results = verify_evidence_in_data(evidence, lead_data)

        assert len(results) == 2
        assert all(r["valid"] for r in results)

    def test_list_evidence(self):
        """Test verification with list data."""
        lead_data = {
            "tech_stack": ["React", "Node.js", "PostgreSQL"],
            "competitors": ["CompanyA", "CompanyB"],
        }
        evidence = ["React", "CompanyA"]
        results = verify_evidence_in_data(evidence, lead_data)

        assert len(results) == 2
        assert all(r["valid"] for r in results)

    def test_fuzzy_match_above_threshold(self):
        """Test that fuzzy matches above threshold are valid."""
        lead_data = {"description": "Enterprise software company"}
        evidence = ["enterprise software"]
        results = verify_evidence_in_data(evidence, lead_data, threshold=0.7)

        assert len(results) == 1
        assert results[0]["valid"] is True
        assert results[0]["similarity"] >= 0.7


class TestValidateCriteriaNames:
    """Tests for the validate_criteria_names function."""

    def test_all_valid_criteria(self):
        """Test validation with all correct criteria names."""
        expected = ["icp_fit", "buying_intent", "authority", "pain_need", "timing"]
        scores = [{"criteria_name": name} for name in expected]
        results = validate_criteria_names(scores, expected)

        assert len(results) == 5
        assert all(r["valid"] for r in results)

    def test_invalid_criteria_name(self):
        """Test validation with incorrect criteria name."""
        expected = ["icp_fit", "buying_intent", "authority"]
        scores = [{"criteria_name": "icp_fits"}, {"criteria_name": "buying_intent"}]
        results = validate_criteria_names(scores, expected)

        assert len(results) == 2
        assert results[0]["valid"] is False
        assert results[1]["valid"] is True
        assert results[0]["suggestion"] == "icp_fit"

    def test_typo_suggestion(self):
        """Test that suggestions are provided for typos."""
        expected = ["icp_fit", "buying_intent"]
        scores = [{"criteria_name": "icp_ft"}]
        results = validate_criteria_names(scores, expected)

        assert len(results) == 1
        assert results[0]["valid"] is False
        assert results[0]["suggestion"] == "icp_fit"


class TestValidateScoreRanges:
    """Tests for the validate_score_ranges function."""

    def test_valid_scores_and_confidence(self):
        """Test validation with valid score and confidence values."""
        scores = [
            {"score": 7, "confidence": 0.8},
            {"score": 10, "confidence": 1.0},
            {"score": 1, "confidence": 0.0},
        ]
        results = validate_score_ranges(scores)

        assert len(results) == 3
        assert all(r["valid"] for r in results)

    def test_score_out_of_range_high(self):
        """Test validation with score above maximum."""
        scores = [{"score": 11, "confidence": 0.5}]
        results = validate_score_ranges(scores)

        assert len(results) == 1
        assert results[0]["valid"] is False
        assert "out of range" in results[0]["issues"][0]

    def test_score_out_of_range_low(self):
        """Test validation with score below minimum."""
        scores = [{"score": 0, "confidence": 0.5}]
        results = validate_score_ranges(scores)

        assert len(results) == 1
        assert results[0]["valid"] is False

    def test_confidence_out_of_range(self):
        """Test validation with confidence above maximum."""
        scores = [{"score": 5, "confidence": 1.5}]
        results = validate_score_ranges(scores)

        assert len(results) == 1
        assert results[0]["valid"] is False

    def test_missing_values(self):
        """Test validation with missing score or confidence."""
        scores = [
            {"confidence": 0.5},  # Missing score
            {"score": 5},  # Missing confidence
        ]
        results = validate_score_ranges(scores)

        assert len(results) == 2
        assert all(not r["valid"] for r in results)


class TestAntiHallucinationValidator:
    """Tests for the AntiHallucinationValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance with standard criteria."""
        return AntiHallucinationValidator(
            expected_criteria=["icp_fit", "buying_intent", "authority", "pain_need", "timing"],
            evidence_threshold=0.85,
        )

    @pytest.fixture
    def sample_lead_data(self):
        """Create sample lead data for testing."""
        return {
            "email_hash": "abc123",
            "first_name": "John",
            "last_name": "Doe",
            "company": "TechCorp",
            "job_title": "VP of Engineering",
            "industry": "Software",
            "employee_count": 250,
            "tech_stack": ["Python", "AWS", "Kubernetes"],
            "recent_funding": {
                "round": "Series B",
                "amount": 30000000,
                "date": "2024-12",
            },
        }

    def test_valid_llm_result(self, validator, sample_lead_data):
        """Test validation with a fully valid LLM result."""
        llm_result = {
            "lead_email_hash": "abc123",
            "criteria_scores": [
                {
                    "criteria_name": "icp_fit",
                    "score": 8,
                    "reasoning": "Strong match based on company size and industry.",
                    "cited_evidence": ["TechCorp", "Software", "250 employees"],
                    "confidence": 0.9,
                },
                {
                    "criteria_name": "buying_intent",
                    "score": 7,
                    "reasoning": "Recent funding indicates potential budget availability.",
                    "cited_evidence": ["Series B", "$30,000,000"],
                    "confidence": 0.8,
                },
                {
                    "criteria_name": "authority",
                    "score": 9,
                    "reasoning": "VP level role suggests decision-making authority.",
                    "cited_evidence": ["VP of Engineering"],
                    "confidence": 0.95,
                },
                {
                    "criteria_name": "pain_need",
                    "score": 6,
                    "reasoning": "Engineering role may indicate scaling challenges.",
                    "cited_evidence": ["Engineering"],
                    "confidence": 0.7,
                },
                {
                    "criteria_name": "timing",
                    "score": 8,
                    "reasoning": "Recent funding suggests immediate investment capacity.",
                    "cited_evidence": ["Series B", "2024-12"],
                    "confidence": 0.85,
                },
            ],
            "overall_summary": "Strong lead with good fit and timing.",
            "suggested_action": "Schedule discovery call to discuss engineering challenges.",
            "disqualify": False,
            "disqualify_reason": None,
        }

        result = validator.validate(llm_result, sample_lead_data)

        assert result["is_valid"] is True
        assert result["total_checks"] > 0
        assert result["failed_checks"] == 0

    def test_invalid_criteria_names(self, validator, sample_lead_data):
        """Test validation with incorrect criteria names."""
        llm_result = {
            "lead_email_hash": "abc123",
            "criteria_scores": [
                {
                    "criteria_name": "icp_fits",  # Typo
                    "score": 8,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["TechCorp"],
                    "confidence": 0.9,
                },
                {
                    "criteria_name": "buying_intention",  # Wrong name
                    "score": 7,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["Series B"],
                    "confidence": 0.8,
                },
                {
                    "criteria_name": "authority",
                    "score": 9,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["VP of Engineering"],
                    "confidence": 0.95,
                },
                {
                    "criteria_name": "pain_need",
                    "score": 6,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["Engineering"],
                    "confidence": 0.7,
                },
                {
                    "criteria_name": "timing",
                    "score": 8,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["2024-12"],
                    "confidence": 0.85,
                },
            ],
            "overall_summary": "Summary here.",
            "suggested_action": "Call them.",
            "disqualify": False,
            "disqualify_reason": None,
        }

        result = validator.validate(llm_result, sample_lead_data)

        assert result["is_valid"] is False
        assert result["criteria_validation"][0]["valid"] is False
        assert result["criteria_validation"][1]["valid"] is False

    def test_hallucinated_evidence(self, validator, sample_lead_data):
        """Test validation with fabricated evidence."""
        llm_result = {
            "lead_email_hash": "abc123",
            "criteria_scores": [
                {
                    "criteria_name": "icp_fit",
                    "score": 8,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["Fortune 500 company", "CEO decision maker"],  # Hallucinated
                    "confidence": 0.9,
                },
                {
                    "criteria_name": "buying_intent",
                    "score": 7,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["Demo request last week"],  # Hallucinated
                    "confidence": 0.8,
                },
                {
                    "criteria_name": "authority",
                    "score": 9,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["VP of Engineering"],
                    "confidence": 0.95,
                },
                {
                    "criteria_name": "pain_need",
                    "score": 6,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["Engineering"],
                    "confidence": 0.7,
                },
                {
                    "criteria_name": "timing",
                    "score": 8,
                    "reasoning": "This reasoning is long enough to pass validation checks here.",
                    "cited_evidence": ["2024-12"],
                    "confidence": 0.85,
                },
            ],
            "overall_summary": "Summary here.",
            "suggested_action": "Call them.",
            "disqualify": False,
            "disqualify_reason": None,
        }

        result = validator.validate(llm_result, sample_lead_data)

        assert result["is_valid"] is False
        # Should have failed evidence checks
        failed_evidence = sum(1 for r in result["evidence_validation"] if not r["valid"])
        assert failed_evidence >= 2
