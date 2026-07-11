// API Types - Generated from FastAPI Pydantic schemas

export interface CriteriaScore {
  criteria_name: string;
  score: number;
  reasoning: string;
  cited_evidence: string[];
  confidence: number;
}

export interface LeadScoreResult {
  lead_email_hash: string;
  criteria_scores: CriteriaScore[];
  overall_summary: string;
  suggested_action: string;
  disqualify: boolean;
  disqualify_reason?: string | null;
}

export interface CompositeScore {
  id: string;
  lead_id: string;
  composite_score: number;
  overall_summary: string;
  suggested_action: string;
  disqualify: boolean;
  disqualify_reason?: string | null;
  created_at: string;
}

export interface Lead {
  id: string;
  email: string;
  email_hash: string;
  first_name: string;
  last_name: string;
  company: string;
  company_domain: string;
  job_title: string;
  source: string;
  status: 'new' | 'enriched' | 'scored' | 'digested' | 'disqualified';
  raw_payload: Record<string, unknown>;
  enriched_data?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  composite_score?: CompositeScore | null;
  scores?: CriteriaScoreRead[] | null;
}

export interface CriteriaScoreRead {
  id: string;
  criteria_name: string;
  score: number;
  reasoning?: string | null;
  cited_evidence?: string[] | null;
  confidence: number;
  created_at: string;
}

export interface LeadListResponse {
  success: boolean;
  data: Lead[];
  meta: {
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  };
}

export interface CriteriaConfig {
  id: string;
  name: string;
  display_name: string;
  description: string;
  weight: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CriteriaConfigListResponse {
  success: boolean;
  data: CriteriaConfig[];
}

export interface DigestRun {
  id: string;
  run_date: string;
  total_leads: number;
  hot_count: number;
  warm_count: number;
  cold_count: number;
  email_sent_at?: string | null;
  slack_sent_at?: string | null;
  status: 'pending' | 'sent' | 'failed';
  error_message?: string | null;
}

export interface DigestPayload {
  success: boolean;
  data: {
    date: string;
    total_processed: number;
    hot_count: number;
    warm_count: number;
    cold_count: number;
    hot_leads: Lead[];
    warm_leads: Lead[];
  };
}

export interface StandardResponse<T = unknown> {
  success: boolean;
  data: T;
  meta?: Record<string, unknown>;
  error?: string;
}
