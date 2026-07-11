"""Meta-prompts for the AI Lead Scoring Agent.

This module contains all system and user prompts used by the LangGraph agent
for scoring sales leads. Prompts are designed to minimize hallucination and
ensure consistent, actionable output.
"""

CRITERIA_DEFINITIONS = {
    "icp_fit": """Ideal Customer Profile (ICP) Fit:
- Does the company match our target industry, size, and geography?
- Is the contact at an appropriate decision-making level?
- Score 10: Perfect match on all dimensions. Score 1: Complete mismatch.""",
    "buying_intent": """Buying Intent Signals:
- Has the lead shown interest via website visits, content downloads, or demo requests?
- Are they actively researching solutions in our category?
- Score 10: Strong, recent intent signals. Score 1: No observable intent.""",
    "authority": """Decision-Maker Authority:
- Does this person have budget authority or strong influence?
- Are they a C-level executive, VP, or director with purchasing power?
- Score 10: Clear economic buyer. Score 1: No decision authority.""",
    "pain_need": """Pain Point & Need Identification:
- Is there a clear, articulated business problem we can solve?
- Does the lead's role suggest they experience this pain acutely?
- Score 10: Severe, well-documented pain. Score 1: No apparent need.""",
    "timing": """Timing & Urgency:
- Is there a compelling event driving purchase timing (e.g., funding, leadership change)?
- Are they evaluating solutions within the next 90 days?
- Score 10: Immediate need with budget allocated. Score 1: No timeline indicated.""",
}

SYSTEM_PROMPT = f"""You are an expert B2B sales qualification assistant. Your task is to score sales leads 
based on five specific criteria using ONLY the data provided in the lead record.

## CRITICAL RULES - ANTI-HALLUCINATION:
1. NEVER invent, assume, or fabricate any information not explicitly present in the lead data.
2. If data is missing for a criterion, state "Insufficient data" and assign a low confidence score.
3. All cited_evidence must be EXACT quotes or data points from the provided lead record.
4. Do not use external knowledge about companies or people unless it is in the provided data.
5. If you cannot find evidence for a score, lower the score and confidence accordingly.

## SCORING CRITERIA:
{chr(10).join(f"- {name}: {desc}" for name, desc in CRITERIA_DEFINITIONS.items())}

## OUTPUT REQUIREMENTS:
1. You MUST output valid JSON matching the LeadScoreResult schema exactly.
2. You MUST provide exactly 5 criteria_scores, one for each criterion defined above.
3. Each criteria_score must have: criteria_name, score (1-10), reasoning (20-300 chars), 
   cited_evidence (list of exact quotes), confidence (0.0-1.0).
4. overall_summary must be 2-3 sentences written for a sales rep, avoiding jargon.
5. suggested_action must be ONE specific, actionable next step (e.g., "Send personalized email 
   referencing their recent Series B funding and ask about scaling their SDR team").
6. Set disqualify=true if the weighted composite score would be below 40.
7. lead_email_hash must be copied exactly from the input.

Respond ONLY with the JSON object. No preamble, no markdown, no explanations."""


def build_user_prompt(lead_data: dict, criteria_configs: list[dict]) -> str:
    """Build the user prompt for scoring a specific lead.

    Args:
        lead_data: Dictionary containing enriched lead information.
        criteria_configs: List of criteria configurations with weights.

    Returns:
        Formatted user prompt string.
    """
    # Format criteria configs for reference
    criteria_context = "\n".join(
        f"- {c['name']}: weight={c['weight']}, active={c['is_active']}"
        for c in criteria_configs
    )

    # Format lead data as readable text
    lead_text = []
    lead_text.append(f"Lead Email Hash: {lead_data.get('email_hash', 'N/A')}")
    lead_text.append(f"Name: {lead_data.get('first_name', '')} {lead_data.get('last_name', '')}")
    lead_text.append(f"Job Title: {lead_data.get('job_title', 'N/A')}")
    lead_text.append(f"Company: {lead_data.get('company', 'N/A')}")
    lead_text.append(f"Domain: {lead_data.get('company_domain', 'N/A')}")
    lead_text.append(f"Industry: {lead_data.get('industry', 'N/A')}")
    lead_text.append(f"Employee Count: {lead_data.get('employee_count', 'N/A')}")
    lead_text.append(f"Headquarters: {lead_data.get('headquarters', 'N/A')}")
    lead_text.append(f"LinkedIn: {lead_data.get('linkedin_url', 'N/A')}")
    lead_text.append(f"Tech Stack: {', '.join(lead_data.get('tech_stack', [])) or 'N/A'}")
    
    if lead_data.get('recent_funding'):
        funding = lead_data['recent_funding']
        lead_text.append(f"Recent Funding: {funding.get('round', '')} - ${funding.get('amount', 0):,} ({funding.get('date', '')})")
    
    lead_text.append(f"Source: {lead_data.get('source', 'N/A')}")
    lead_text.append(f"Status: {lead_data.get('status', 'N/A')}")

    return f"""Score the following lead based on the criteria and weights provided.

## Active Criteria Weights:
{criteria_context}

## Lead Record:
{chr(10).join(lead_text)}

## Raw Payload Data (for additional context):
{lead_data.get('raw_payload', {})}

Remember: Use ONLY the data above. If information is missing, acknowledge it and adjust 
your score and confidence accordingly. Output valid JSON only."""
