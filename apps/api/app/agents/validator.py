"""Anti-hallucination validator for LLM outputs.

This module provides validation logic to ensure LLM-generated scores are grounded
in the actual lead data, using fuzzy string matching to verify cited evidence.
"""

from difflib import SequenceMatcher
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def normalize_text(text: str) -> str:
    """Normalize text for comparison by lowercasing and removing extra whitespace.

    Args:
        text: Raw text string to normalize.

    Returns:
        Normalized text string.
    """
    return " ".join(text.lower().split())


def calculate_similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings using SequenceMatcher.

    Args:
        a: First string to compare.
        b: Second string to compare.

    Returns:
        Similarity ratio between 0.0 and 1.0.
    """
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def verify_evidence_in_data(evidence: list[str], lead_data: dict, threshold: float = 0.85) -> list[dict]:
    """Verify that each piece of cited evidence exists in the lead data.

    Args:
        evidence: List of evidence strings cited by the LLM.
        lead_data: Dictionary containing the original lead data.
        threshold: Minimum similarity ratio to consider evidence valid.

    Returns:
        List of validation results for each evidence item.
    """
    # Flatten lead data into searchable text
    searchable_texts = []
    
    def extract_values(obj: Any, depth: int = 0) -> None:
        """Recursively extract all string values from nested structures."""
        if depth > 5:  # Prevent infinite recursion
            return
        if isinstance(obj, str):
            searchable_texts.append(normalize_text(obj))
        elif isinstance(obj, dict):
            for value in obj.values():
                extract_values(value, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                extract_values(item, depth + 1)
    
    extract_values(lead_data)
    combined_text = " ".join(searchable_texts)
    
    results = []
    for idx, evid in enumerate(evidence):
        normalized_evidence = normalize_text(evid)
        
        # Check for exact substring match first
        if normalized_evidence in combined_text:
            results.append({
                "index": idx,
                "evidence": evid,
                "valid": True,
                "similarity": 1.0,
                "reason": "Exact match found",
            })
            continue
        
        # Fall back to fuzzy matching against individual fields
        max_similarity = 0.0
        best_match_field = None
        
        for text in searchable_texts:
            sim = calculate_similarity(normalized_evidence, text)
            if sim > max_similarity:
                max_similarity = sim
                best_match_field = text[:50]  # Truncate for logging
        
        is_valid = max_similarity >= threshold
        results.append({
            "index": idx,
            "evidence": evid,
            "valid": is_valid,
            "similarity": max_similarity,
            "reason": f"Similarity {max_similarity:.2f} vs threshold {threshold}" 
                      if not is_valid else f"Matched field: {best_match_field}",
        })
        
        if not is_valid:
            logger.warning(
                "Evidence validation failed",
                evidence=evid,
                similarity=max_similarity,
                threshold=threshold,
            )
    
    return results


def validate_criteria_names(
    criteria_scores: list[dict], 
    expected_criteria: list[str]
) -> list[dict]:
    """Validate that all criteria names match expected values exactly.

    Args:
        criteria_scores: List of criteria score dictionaries from LLM.
        expected_criteria: List of expected criteria names.

    Returns:
        List of validation results for each criteria name.
    """
    results = []
    
    for idx, score in enumerate(criteria_scores):
        provided_name = score.get("criteria_name", "")
        is_valid = provided_name in expected_criteria
        
        # If invalid, suggest closest match
        suggestion = None
        if not is_valid:
            best_match = max(
                expected_criteria,
                key=lambda x: calculate_similarity(provided_name, x),
                default=None,
            )
            if best_match and calculate_similarity(provided_name, best_match) > 0.6:
                suggestion = best_match
        
        results.append({
            "index": idx,
            "provided_name": provided_name,
            "valid": is_valid,
            "suggestion": suggestion,
        })
        
        if not is_valid:
            logger.warning(
                "Criteria name mismatch",
                provided=provided_name,
                expected=expected_criteria,
                suggestion=suggestion,
            )
    
    return results


def validate_score_ranges(criteria_scores: list[dict]) -> list[dict]:
    """Validate that all scores are within acceptable ranges.

    Args:
        criteria_scores: List of criteria score dictionaries from LLM.

    Returns:
        List of validation results for each score.
    """
    results = []
    
    for idx, score in enumerate(criteria_scores):
        score_value = score.get("score")
        confidence = score.get("confidence")
        
        issues = []
        
        if score_value is None:
            issues.append("score is missing")
        elif not (1 <= score_value <= 10):
            issues.append(f"score {score_value} out of range [1, 10]")
        
        if confidence is None:
            issues.append("confidence is missing")
        elif not (0.0 <= confidence <= 1.0):
            issues.append(f"confidence {confidence} out of range [0.0, 1.0]")
        
        is_valid = len(issues) == 0
        results.append({
            "index": idx,
            "valid": is_valid,
            "issues": issues,
            "score": score_value,
            "confidence": confidence,
        })
        
        if not is_valid:
            logger.warning(
                "Score range validation failed",
                index=idx,
                issues=issues,
            )
    
    return results


class AntiHallucinationValidator:
    """Comprehensive validator for LLM scoring outputs.
    
    This validator checks:
    1. All cited evidence exists in the source data
    2. Criteria names match expected values exactly
    3. Scores and confidence values are in valid ranges
    4. Reasoning length constraints are met
    """
    
    def __init__(
        self,
        expected_criteria: list[str],
        evidence_threshold: float = 0.85,
    ):
        """Initialize the validator.
        
        Args:
            expected_criteria: List of expected criteria names.
            evidence_threshold: Minimum similarity ratio for evidence validation.
        """
        self.expected_criteria = expected_criteria
        self.evidence_threshold = evidence_threshold
    
    def validate(self, llm_result: dict, lead_data: dict) -> dict:
        """Run all validation checks on an LLM result.
        
        Args:
            llm_result: Dictionary containing the LLM's scoring output.
            lead_data: Original lead data dictionary.
        
        Returns:
            Validation summary with pass/fail status and detailed results.
        """
        criteria_scores = llm_result.get("criteria_scores", [])
        evidence_list = []
        
        # Collect all evidence from all criteria scores
        for score in criteria_scores:
            evidence_list.extend(score.get("cited_evidence", []))
        
        # Run all validations
        evidence_results = verify_evidence_in_data(
            evidence_list, lead_data, self.evidence_threshold
        )
        criteria_results = validate_criteria_names(criteria_scores, self.expected_criteria)
        score_results = validate_score_ranges(criteria_scores)
        
        # Validate reasoning lengths
        reasoning_results = []
        for idx, score in enumerate(criteria_scores):
            reasoning = score.get("reasoning", "")
            is_valid = 20 <= len(reasoning) <= 300
            reasoning_results.append({
                "index": idx,
                "valid": is_valid,
                "length": len(reasoning),
            })
            if not is_valid:
                logger.warning(
                    "Reasoning length out of bounds",
                    index=idx,
                    length=len(reasoning),
                )
        
        # Determine overall validity
        all_valid = (
            all(r["valid"] for r in evidence_results) and
            all(r["valid"] for r in criteria_results) and
            all(r["valid"] for r in score_results) and
            all(r["valid"] for r in reasoning_results)
        )
        
        return {
            "is_valid": all_valid,
            "evidence_validation": evidence_results,
            "criteria_validation": criteria_results,
            "score_validation": score_results,
            "reasoning_validation": reasoning_results,
            "total_checks": (
                len(evidence_results) + len(criteria_results) + 
                len(score_results) + len(reasoning_results)
            ),
            "failed_checks": sum(
                1 for r in evidence_results + criteria_results + score_results + reasoning_results
                if not r["valid"]
            ),
        }
