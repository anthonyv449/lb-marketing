/**
 * @fileoverview Delta calculation helpers and report text formatter for MonthEndReport.
 * All functions are pure — no side effects.
 */

import { COLORS } from '../shared/styles';

/**
 * Computes the delta between two numeric values and returns a display label + colour.
 * @param {number|string} before
 * @param {number|string} after
 * @param {boolean} invertColor — true for metrics where lower is better (e.g. search position)
 */
export function calcDelta(before, after, invertColor = false) {
  const b = parseFloat(before);
  const a = parseFloat(after);
  if (isNaN(b) || isNaN(a)) return { label: '—', color: COLORS.muted };

  const diff = a - b;
  if (diff === 0) return { label: 'no change', color: COLORS.muted };

  const improved = invertColor ? diff < 0 : diff > 0;
  const sign = diff > 0 ? '+' : '';
  const arrow = improved ? '▲' : '▼';
  const label = `${arrow} ${sign}${diff % 1 === 0 ? diff : diff.toFixed(1)}`;
  const color = improved ? COLORS.green : COLORS.red;
  return { label, color };
}

export function formatReportText(d) {
  const kw1 = calcDelta(d.kw1Before, d.kw1After, true);
  const kw2 = calcDelta(d.kw2Before, d.kw2After, true);
  const rev = calcDelta(d.reviewsBefore, d.reviewsAfter);
  const rat = calcDelta(d.ratingBefore, d.ratingAfter);
  const views = calcDelta(d.viewsBefore, d.viewsAfter);

  return [
    `MONTH-END PERFORMANCE REPORT`,
    `${'═'.repeat(50)}`,
    `Business:     ${d.businessName || '—'}`,
    `Period:       ${d.reportPeriod || '—'}`,
    '',
    `── Search Rankings ─────────────────────────`,
    `${d.keyword1 || 'Keyword 1'}:  ${d.kw1Before || '—'} → ${d.kw1After || '—'}  (${kw1.label})`,
    `${d.keyword2 || 'Keyword 2'}:  ${d.kw2Before || '—'} → ${d.kw2After || '—'}  (${kw2.label})`,
    '',
    `── Reviews ─────────────────────────────────`,
    `Count:   ${d.reviewsBefore || '—'} → ${d.reviewsAfter || '—'}  (${rev.label})`,
    `Rating:  ${d.ratingBefore || '—'} → ${d.ratingAfter || '—'}  (${rat.label})`,
    '',
    `── Profile Views ───────────────────────────`,
    `Views:   ${d.viewsBefore || '—'} → ${d.viewsAfter || '—'}  (${views.label})`,
    '',
    `── What Changed ────────────────────────────`,
    d.changesMade || '(none)',
    '',
    `── Highlights ──────────────────────────────`,
    d.highlights || '(none)',
    '',
    `── Month 2 Plan ────────────────────────────`,
    d.month2Plan || '(none)',
    '',
    `${'─'.repeat(50)}`,
    `Report generated ${new Date().toLocaleDateString()}`,
  ].join('\n');
}
