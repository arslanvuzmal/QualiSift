"""Pydantic schemas for LLM scoring outputs."""

from pydantic import BaseModel, Field


class CriteriaScore(BaseModel):
    """Schema for individual criteria scoring from LLM."""

    criteria_name: str = Field(
        description="Must match configured criteria names exactly (e.g., 'icp_fit')"
    )
    score: int = Field(ge=1, le=10, description="Score from 1 (worst) to 10 (best)")
    reasoning: str = Field(
        min_length=20,
        max_length=300,
        description="Plain-language explanation. No jargon.",
    )
    cited_evidence: list[str] = Field(
        description="Exact quotes/data points from the lead record supporting this score."
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence based on available data."
    )


class LeadScoreResult(BaseModel):
    """Schema for complete lead scoring result from LLM."""

    lead_email_hash: str = Field(description="Hashed email of the scored lead")
    criteria_scores: list[CriteriaScore] = Field(
        min_length=5, max_length=5, description="Scores for all 5 criteria"
    )
    overall_summary: str = Field(
        min_length=30,
        max_length=500,
        description="2-3 sentence summary for the sales rep.",
    )
    suggested_action: str = Field(
        description="ONE specific, actionable next step."
    )
    disqualify: bool = Field(description="True if composite score < 40")
    disqualify_reason: str | None = Field(default=None)
