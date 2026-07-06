# Business Impact — Cortex AI Sales Lead Qualifier

> How an agentic lead-qualification layer changes the economics of a sales team.
> Figures below are an **illustrative model** you can re-run with your own numbers;
> the mechanics (time saved, faster response, better prioritization) are the point.

---

## 1. The problem it removes

In most B2B funnels, **reps decide who to call based on gut feel and recency**, not on a
consistent read of fit and intent. The result is a well-documented pattern:

- **~50% of a rep's day** is spent on research, list triage, and admin — not selling.
- **The first vendor to respond wins ~35–50%** of deals, yet median lead response time is measured in **hours**.
- **Lead scoring is inconsistent**: two reps score the same lead differently, and "why" is never recorded.

Cortex attacks all three: it does the research (enrichment), applies **one consistent, weighted
rubric** to every lead in seconds, and records the reasoning + evidence behind each score.

---

## 2. What changes, concretely

| Before Cortex | With Cortex |
|---------------|-------------|
| Reps manually research + guess priority | Every lead auto-enriched and scored 0–100 in seconds |
| "Why is this a good lead?" — no record | Every score cites the exact evidence it used |
| Hot leads wait in a shared queue | Daily **Hot / Warm / Cold** digest surfaces the top ~20% |
| Scoring rubric lives in someone's head | Five weighted criteria, tunable by sales ops in the UI |
| LLM outputs trusted blindly | Anti-hallucination validator rejects ungrounded claims |

---

## 3. Illustrative ROI model

Assume a **10-rep** team, each handling **40 inbound leads/week**, fully-loaded cost **$120k/rep/yr**
(~$1.15/min), average deal **$12,000**, baseline win rate **4%**.

**Time reclaimed (prioritization + research automation)**

| Item | Estimate |
|------|----------|
| Manual triage/research saved per lead | ~6 min |
| Leads / week (team) | 400 |
| Time saved / week | ~40 hours |
| Time saved / year | ~2,000 hours |
| **Value of reclaimed selling time / year** | **~$138,000** |

**Conversion lift (faster response + focus on Hot leads)**

| Item | Estimate |
|------|----------|
| Leads / year | ~20,800 |
| Deals at 4% baseline | 832 → **$9.98M** |
| Deals at 4.6% (＋0.6pt from faster, prioritized follow-up) | 957 → **$11.48M** |
| **Incremental revenue / year** | **~$1.5M** |

Even if you discount these by 60%, the payback on a mock-mode pilot (effectively **$0 in API spend**)
is immediate. In production, the only variable cost is LLM + enrichment calls — cents per lead.

---

## 4. Where it creates leverage

- **Faster speed-to-lead** — new leads are scored the moment they arrive (background task), so reps
  get a ranked list instead of a raw queue.
- **Consistent, auditable qualification** — the same rubric, every time, with the evidence attached.
  Great for coaching, forecasting, and compliance.
- **Sales-ops control without engineering** — criteria weights are tuned in the UI and take effect on
  the next scoring run.
- **No lock-in, no key required to evaluate** — swap OpenAI ⇄ mock, Clearbit ⇄ mock via config; pilot
  entirely offline, then wire up real providers.

---

## 5. Risk controls built in

- **PII minimization** — emails are SHA-256 hashed and phones masked *before* any LLM call.
- **Anti-hallucination** — cited evidence is verified (string + numeric matching) against the source
  record; ungrounded scores are flagged, not trusted.
- **Structured outputs** — the LLM must return a strict Pydantic schema; free-text JSON is never parsed.
- **Graceful degradation** — missing API keys fall back to deterministic mock providers instead of failing.

---

## 6. Adoption path

1. **Pilot (week 1):** run in mock mode on a sample of real leads; validate the rubric and the digest.
2. **Wire providers (week 2):** set `LLM_PROVIDER=openai` and `ENRICHMENT_PROVIDER=clearbit`.
3. **Integrate intake (week 3):** point HubSpot/Marketo webhooks at `/api/v1/webhooks/inbound`.
4. **Operationalize:** schedule the daily digest to email + Slack; let sales ops own the weights.

The whole stack runs from a single `docker compose up`, so a pilot is a same-day exercise.
