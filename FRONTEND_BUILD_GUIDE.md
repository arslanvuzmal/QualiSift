# 🎨 Frontend Build Guide - AI Sales Lead Qualifier

## 📋 Project Context

**AI Sales Lead Qualifier** is an intelligent lead scoring platform that uses LLMs to evaluate and rank sales leads based on customizable criteria. The system enriches lead data, scores leads using AI agents, and delivers daily digests via email and Slack.

### Tech Stack
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS
- **State Management:** SWR for data fetching
- **Charts:** Recharts
- **Icons:** Lucide React
- **API:** FastAPI backend (REST)

---

## ✅ Current State (Phase 7 Complete)

The following has been implemented and is ready for extension:

### Core Infrastructure
- ✅ Next.js 14 App Router structure with TypeScript
- ✅ Tailwind CSS configured with professional color palette
- ✅ Sidebar navigation layout (Dashboard, Criteria, Digest, Setup)
- ✅ All dependencies installed: `recharts`, `swr`, `lucide-react`, `clsx`, `tailwind-merge`

### API Layer (`src/lib/`)
- ✅ `types.ts` - Complete TypeScript interfaces matching backend Pydantic schemas
  - `Lead`, `CriteriaScore`, `CompositeScore`, `CriteriaConfig`, `DigestRun`
  - `StandardResponse<T>` wrapper for all API responses
- ✅ `api.ts` - Typed fetch wrapper with error handling
  - Functions: `fetchLeads`, `fetchLead`, `createLead`, `scoreLead`, `fetchCriteria`, `updateCriteria`, `generateDigest`, `fetchDigestHistory`, `checkHealth`, `saveConfig`
- ✅ `hooks.ts` - SWR hooks for reactive data fetching
  - `useLeads()`, `useCriteria()`, `useDigestHistory()`, `useHealth()`
- ✅ `utils.ts` - Utility functions including `cn()` for class merging

### UI Components (`src/components/`)
- ✅ `ScoreBadge.tsx` - Color-coded score badge (Red: 75-100, Amber: 40-74, Slate: 0-39)
- ✅ `ScoreRadar.tsx` - Responsive radar chart showing 5 criteria scores
- ✅ `LeadCard.tsx` - Expandable card with lead details and composite score
- ✅ `CriteriaEditor.tsx` - Weight adjustment form with validation (must sum to 1.0)

### Pages (`src/app/`)
- ✅ `/` (Dashboard) - Leads table with stats, refresh, and digest generation
- ✅ `/setup` (Setup Wizard) - 5-step configuration form (LLM, Enrichment, CRM, Email, Company)
- ✅ `layout.tsx` - Root layout with sidebar navigation

---

## 🚀 Next Steps for Antigravity IDE

Use this guide to build the remaining pages and features. Follow the order below for optimal development flow.

### Priority 1: Lead Detail Page

**Route:** `/leads/[id]/page.tsx`

**Requirements:**
```tsx
// Use these existing components
import { ScoreRadar } from '@/components/ScoreRadar';
import { ScoreBadge } from '@/components/ScoreBadge';
import { useLead } from '@/lib/hooks'; // You'll need to add this hook

// Features to implement:
// 1. Fetch single lead by ID using api.fetchLead(id)
// 2. Display full lead information in a card layout
// 3. Show ScoreRadar with the lead's 5 criteria scores
// 4. Display cited evidence as a list
// 5. Show overall_summary and suggested_action prominently
// 6. Add "Re-score" button that calls api.scoreLead(id)
// 7. Add "Disqualify" button with reason input
```

**Design Notes:**
- Use a two-column layout: left for lead info, right for scoring visualization
- Evidence items should be in `<blockquote>` style boxes with blue left border
- Action buttons should be in a fixed footer bar at bottom

---

### Priority 2: Criteria Management Page

**Route:** `/criteria/page.tsx`

**Requirements:**
```tsx
import { CriteriaEditor } from '@/components/CriteriaEditor';
import { useCriteria } from '@/lib/hooks';

// Features:
// 1. List all criteria configs in a table
// 2. Click to edit opens CriteriaEditor modal/slide-over
// 3. Save updates via api.updateCriteria(id, data)
// 4. Show visual warning if weights don't sum to 1.0
// 5. Add "Reset to Defaults" button
```

**Design Notes:**
- Table columns: Name, Description, Weight, Active Status, Actions
- Use amber alert banner when weights are invalid
- Success toast on save

---

### Priority 3: Digest History Page

**Route:** `/digest/page.tsx`

**Requirements:**
```tsx
import { useDigestHistory } from '@/lib/hooks';

// Features:
// 1. Table of past digest runs (date, total, hot/warm/cold counts, status)
// 2. Click row to view digest details (modal or separate page)
// 3. Status badges: pending (gray), sent (green), failed (red)
// 4. "Regenerate" button for failed digests
// 5. "View Email Preview" button to see rendered HTML
```

**Design Notes:**
- Use alternating row colors for readability
- Date column should show relative time (e.g., "2 hours ago")
- Add date range filter at top

---

### Priority 4: Dashboard Enhancements

**Route:** `/page.tsx` (enhance existing)

**Features to Add:**
```tsx
// 1. Add filtering by status (dropdown: All, New, Scored, Digested, Disqualified)
// 2. Add sorting by score (ascending/descending)
// 3. Add search box for company name or email
// 4. Add bulk actions checkbox column
// 5. Add "Export to CSV" button
// 6. Show loading skeleton while fetching
```

**Search Implementation Example:**
```tsx
const [searchTerm, setSearchTerm] = useState('');
const filteredLeads = leads.filter(
  (lead) =>
    lead.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.email.toLowerCase().includes(searchTerm.toLowerCase())
);
```

---

### Priority 5: Add Lead Modal

**Component:** `src/components/AddLeadModal.tsx`

**Requirements:**
```tsx
// Form fields:
// - Email (required, email validation)
// - First Name, Last Name
// - Company
// - Company Domain
// - Job Title
// - Source (dropdown: Manual, Webhook, Import, Other)
// - Raw Payload (JSON textarea, optional)

// On submit:
// 1. Validate form
// 2. Call api.createLead(data)
// 3. Close modal and refresh leads list
// 4. Show success/error toast
```

---

## 🎨 Design System Rules

### Color Palette
```typescript
// Primary Actions
bg-indigo-600 hover:bg-indigo-700 text-white

// Neutral Backgrounds
bg-slate-50  // Page background
bg-white     // Cards, panels
bg-slate-900 // Sidebar

// Score Colors
bg-rose-100 text-rose-800 border-rose-200  // Hot (75-100)
bg-amber-100 text-amber-800 border-amber-200  // Warm (40-74)
bg-slate-100 text-slate-800 border-slate-200  // Cold (0-39)

// Status Colors
bg-emerald-100 text-emerald-800  // Success/Sent
bg-amber-100 text-amber-800      // Warning/Pending
bg-rose-100 text-rose-800        // Error/Failed
```

### Typography
```tsx
// Headings
text-2xl font-bold text-slate-900  // Page titles
text-lg font-semibold text-slate-900  // Section headers

// Body
text-sm text-slate-600  // Regular text
text-xs text-slate-500  // Captions, metadata
```

### Spacing Scale
- Use Tailwind's default scale: `p-4`, `m-6`, `gap-4`, etc.
- Avoid arbitrary values like `p-[17px]`
- Consistent section padding: `p-6` or `p-8`

### Component Patterns
```tsx
// Card container
<div className="bg-white border rounded-lg shadow-sm">

// Button variants
<button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">  // Primary
<button className="px-4 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">  // Secondary
<button className="px-4 py-2 text-rose-600 hover:bg-rose-50 rounded-lg">  // Danger

// Input fields
<input className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent" />
```

---

## 📡 API Reference

### Available Functions

```typescript
// Leads
await fetchLeads(page, perPage)  // Returns StandardResponse<{ data: Lead[], meta: ... }>
await fetchLead(id)              // Returns StandardResponse<Lead>
await createLead(data)           // Returns StandardResponse<Lead>
await scoreLead(id)              // Returns StandardResponse<{ status: 'queued' }>

// Criteria
await fetchCriteria()            // Returns StandardResponse<CriteriaConfig[]>
await updateCriteria(id, data)   // Returns StandardResponse<CriteriaConfig>

// Digest
await generateDigest()           // Returns StandardResponse<DigestPayload>
await fetchDigestHistory()       // Returns StandardResponse<DigestRun[]>

// Health
await checkHealth()              // Returns StandardResponse<{ db: 'ok', redis: 'ok' }>

// Config
await saveConfig(data)           // Returns StandardResponse<void>
```

### Error Handling
```typescript
try {
  const result = await fetchLeads();
} catch (error) {
  if (error instanceof ApiError) {
    console.error(error.status, error.message);
    // Show user-facing error message
  }
}
```

---

## 🔧 Development Tips

### Running the Frontend
```bash
cd apps/web
npm run dev  # Runs on http://localhost:3001
```

### Environment Variables
Create `.env.local` in `apps/web/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Adding New Hooks
```typescript
// src/lib/hooks.ts
export function useNewFeature() {
  const { data, error, isLoading, mutate } = useSWR<YourType>(
    '/api/v1/your-endpoint',
    (url) => apiClient.get(url)
  );

  return {
    data: data?.data,
    isLoading,
    isError: error,
    mutate,
  };
}
```

### Component Best Practices
1. Always use `'use client'` at top for interactive components
2. Keep server components for static content where possible
3. Use TypeScript strict types (no `any`)
4. Extract complex logic into custom hooks
5. Use `cn()` utility for conditional classes

---

## 📁 File Structure Reference

```
apps/web/src/
├── app/
│   ├── layout.tsx          # Root layout with sidebar
│   ├── page.tsx            # Dashboard
│   ├── setup/
│   │   └── page.tsx        # Setup wizard
│   ├── leads/
│   │   └── [id]/
│   │       └── page.tsx    # TODO: Lead detail page
│   ├── criteria/
│   │   └── page.tsx        # TODO: Criteria management
│   └── digest/
│       └── page.tsx        # TODO: Digest history
├── components/
│   ├── ScoreBadge.tsx      # Score badge component
│   ├── ScoreRadar.tsx      # Radar chart component
│   ├── LeadCard.tsx        # Lead card component
│   ├── CriteriaEditor.tsx  # Criteria weight editor
│   └── AddLeadModal.tsx    # TODO: Add lead modal
└── lib/
    ├── types.ts            # TypeScript interfaces
    ├── api.ts              # API client
    ├── hooks.ts            # SWR hooks
    └── utils.ts            # Utilities (cn function)
```

---

## 🎯 Quick Start Commands

After implementing new pages, verify with:

```bash
# Type check
npm run type-check

# Lint
npm run lint

# Build (production test)
npm run build

# Start dev server
npm run dev
```

---

## 🆘 Troubleshooting

### Hydration Errors
If you see "Hydration failed" warnings:
1. Wrap client-only components with `dynamic(() => import(...), { ssr: false })`
2. Ensure all `useState` and `useEffect` are in `'use client'` components

### API Connection Issues
1. Verify `NEXT_PUBLIC_API_URL` is set correctly
2. Ensure backend is running on the specified port
3. Check CORS settings in backend

### TypeScript Errors
1. Run `npm run type-check` to see all errors
2. Ensure all imports have correct paths (`@/` alias)
3. Check that all interface properties match API response

---

**Happy Building! 🚀**

For questions or issues, refer to the project documentation in `/docs` or check the backend API docs at `http://localhost:8000/docs`.
