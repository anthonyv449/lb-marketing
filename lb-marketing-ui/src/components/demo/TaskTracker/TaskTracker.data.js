/**
 * @fileoverview Week-by-week task definitions and vertical-specific extras
 * for the Demo TaskTracker.
 */

export const WEEKS = [
  {
    week: 1,
    label: 'Week 1',
    theme: 'Discovery & Audit',
    deliverable: 'Initial Audit Report',
    tasks: [
      { id: 'w1_onboarding_call',      text: 'Complete onboarding call',             critical: true },
      { id: 'w1_gbp_access',           text: 'Secure GBP access',                    critical: true },
      { id: 'w1_collect_emails',        text: 'Collect customer email list',          critical: true },
      { id: 'w1_audit_gbp',            text: 'Audit Google Business Profile',        critical: false },
      { id: 'w1_audit_listings',        text: 'Audit other local listings',           critical: false },
      { id: 'w1_review_reviews',        text: 'Review existing reviews',              critical: false },
      { id: 'w1_local_rankings',        text: 'Check local search rankings',          critical: false },
      { id: 'w1_competitor_gap',        text: 'Competitor gap analysis',              critical: false },
      { id: 'w1_deliver_audit',         text: 'Deliver audit report to client',       critical: true },
    ],
  },
  {
    week: 2,
    label: 'Week 2',
    theme: 'Foundation & Quick Wins',
    deliverable: 'Optimised GBP Profile',
    tasks: [
      { id: 'w2_complete_gbp',         text: 'Complete all GBP fields',                      critical: true },
      { id: 'w2_respond_reviews',       text: 'Respond to all unanswered reviews',            critical: true },
      { id: 'w2_review_process',        text: 'Set up review response process',               critical: false },
      { id: 'w2_booking_link',          text: 'Add booking / appointment link',               critical: false },
      { id: 'w2_quickwin_seo',          text: 'Apply quick-win SEO improvements',             critical: false },
      { id: 'w2_services_section',      text: 'Build GBP services section',                   critical: false },
      { id: 'w2_citation_corrections',  text: 'Correct citation inconsistencies',             critical: false },
    ],
  },
  {
    week: 3,
    label: 'Week 3',
    theme: 'Content & Review Generation',
    deliverable: 'First Published Content + Review Requests Sent',
    tasks: [
      { id: 'w3_first_content',         text: 'Publish first content piece',                  critical: true },
      { id: 'w3_review_campaign',        text: 'Launch review generation campaign',            critical: true },
      { id: 'w3_personalised_requests',  text: 'Send personalised review requests',            critical: false },
      { id: 'w3_keyword_baseline',       text: 'Establish keyword ranking baseline',           critical: false },
      { id: 'w3_monitor_followup',       text: 'Monitor and follow up on requests',           critical: false },
    ],
  },
  {
    week: 4,
    label: 'Week 4',
    theme: 'Reporting & Handoff',
    deliverable: 'Month-End Performance Report',
    tasks: [
      { id: 'w4_before_after',          text: 'Collect before/after data',                    critical: true },
      { id: 'w4_count_reviews',          text: 'Count new reviews vs baseline',                critical: false },
      { id: 'w4_document_changes',       text: 'Document GBP changes made',                   critical: false },
      { id: 'w4_calc_rating',            text: 'Calculate rating change',                      critical: false },
      { id: 'w4_write_report',           text: 'Write month-end report',                       critical: true },
      { id: 'w4_present_report',         text: 'Present report to client',                     critical: false },
      { id: 'w4_month2_plan',            text: 'Outline Month 2 plan',                         critical: false },
    ],
  },
];

export const VERTICAL_EXTRAS = {
  salons_spas: {
    label: 'Salons & Spas Extras',
    weeks: [2, 3],
    items: [
      { id: 'vs_ig_audit',         text: 'Instagram audit done' },
      { id: 'vs_ig_posts',         text: '4 Instagram posts published' },
      { id: 'vs_gbp_photos',       text: 'GBP photos refreshed (10+)' },
      { id: 'vs_competitor_review', text: 'Competitor review gap analysis' },
      { id: 'vs_target_reviews',   text: 'Target 5+ new reviews by Day 30' },
    ],
  },
  legal: {
    label: 'Legal & Professional Services Extras',
    weeks: [2, 3],
    items: [
      { id: 'vl_keyword_baseline', text: 'Keyword baseline for top 5 practice-area + city terms' },
      { id: 'vl_gbp_services',     text: 'GBP services built out' },
      { id: 'vl_onpage_seo',       text: 'On-page SEO review done' },
      { id: 'vl_review_process',   text: 'Review request process set up' },
      { id: 'vl_map_pack',         text: 'Target: map pack entry for 1 core keyword' },
    ],
  },
  home_services: {
    label: 'Home Services Extras',
    weeks: [2, 3],
    items: [
      { id: 'vh_gbp_build',        text: 'Full GBP build-out' },
      { id: 'vh_citation_audit',   text: 'Citation audit done' },
      { id: 'vh_keyword_baseline', text: 'Top 5 high-intent keyword baseline' },
      { id: 'vh_review_campaign',  text: 'Review campaign for job completions' },
      { id: 'vh_map_pack',         text: 'Target: map pack appearance for 1 core keyword' },
    ],
  },
};
