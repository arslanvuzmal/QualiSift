/**
 * Minimal CSV reader for lead import: header row, comma-separated, double quotes for fields that
 * contain commas or quotes ("" inside quotes is a literal quote). Enough for exports from a CRM or
 * a spreadsheet; not a general CSV library.
 */
export function parseCsv(text: string): Record<string, string>[] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = '';
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i++;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ',') {
      row.push(field);
      field = '';
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++;
      row.push(field);
      rows.push(row);
      row = [];
      field = '';
    } else {
      field += ch;
    }
  }
  if (field !== '' || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  const nonEmpty = rows.filter((r) => r.some((c) => c.trim() !== ''));
  if (nonEmpty.length === 0) return [];
  const header = nonEmpty[0].map((h) => h.trim().toLowerCase());
  return nonEmpty.slice(1).map((r) => Object.fromEntries(header.map((h, j) => [h, (r[j] ?? '').trim()])));
}

/** The LeadCreate fields the API accepts; other columns are kept as the raw payload. */
export const LEAD_FIELDS = ['email', 'first_name', 'last_name', 'company', 'company_domain', 'job_title', 'source'] as const;

export function toLead(row: Record<string, string>) {
  const lead: Record<string, unknown> = {};
  for (const f of LEAD_FIELDS) if (row[f]) lead[f] = row[f];
  lead.source = lead.source ?? 'csv';
  lead.raw_payload = row;
  return lead;
}
