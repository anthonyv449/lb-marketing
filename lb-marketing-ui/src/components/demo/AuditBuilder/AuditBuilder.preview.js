/**
 * @fileoverview Pure function that generates a formatted multi-line audit report string.
 * No side effects — takes data object, returns text.
 */

export function generateAuditReport(d) {
  return [
    `LOCAL BUSINESS AUDIT REPORT`,
    `${'═'.repeat(50)}`,
    `Business:    ${d.businessName || '—'}`,
    `Audited By:  ${d.auditedBy || '—'}`,
    `Date:        ${d.dateDelivered || '—'}`,
    '',
    `── Google Business Profile ──────────────────`,
    `Status:      ${d.gbpStatus || '—'}`,
    `Photos:      ${d.gbpPhotos || '—'}`,
    `Star Rating: ${d.starRating || '—'}`,
    `Reviews:     ${d.reviewCount || '—'}`,
    '',
    `── Local Search Rankings ────────────────────`,
    `${d.keyword1 || 'Keyword 1'}:  Position ${d.position1 || '—'}`,
    `${d.keyword2 || 'Keyword 2'}:  Position ${d.position2 || '—'}`,
    '',
    `── Website Score ────────────────────────────`,
    `Health Score: ${d.websiteScore || '—'}`,
    '',
    `── Citation Consistency ─────────────────────`,
    `Consistency:  ${d.citationConsistency || '—'}`,
    '',
    `── Top Priority Issues ─────────────────────`,
    `1. ${d.issue1 || '—'}`,
    `2. ${d.issue2 || '—'}`,
    `3. ${d.issue3 || '—'}`,
    '',
    `── Quick Wins ──────────────────────────────`,
    `1. ${d.quickWin1 || '—'}`,
    `2. ${d.quickWin2 || '—'}`,
    '',
    `── Notes ───────────────────────────────────`,
    d.notes || '(none)',
    '',
    `${'─'.repeat(50)}`,
    `Report prepared by ${d.auditedBy || '—'} on ${d.dateDelivered || '—'}`,
  ].join('\n');
}
