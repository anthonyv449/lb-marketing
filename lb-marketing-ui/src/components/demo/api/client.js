/**
 * @fileoverview Centralised backend communication layer for the Demo Toolkit.
 * All Demo Toolkit backend communication flows through this module so UI
 * components remain decoupled from API path and payload details.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const DEFAULT_ENGAGEMENT_ID = import.meta.env.VITE_DEMO_ENGAGEMENT_ID;

// GET /businesses
export async function fetchBusinesses() {
  const url = BASE_URL ? `${BASE_URL}/businesses` : '/businesses';
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch businesses: ${res.status}`);
  }
  return res.json();
}

// GET /businesses/{id}
export async function fetchBusiness(businessId) {
  const url = BASE_URL ? `${BASE_URL}/businesses/${businessId}` : `/businesses/${businessId}`;
  const res = await fetch(url);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error(`Failed to fetch business: ${res.status}`);
  }
  return res.json();
}

function getAuthHeaders() {
  const token = localStorage.getItem('auth_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function resolveEngagementId(input) {
  const value = input || DEFAULT_ENGAGEMENT_ID;
  if (!value) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const err = await response.json();
      message = err.detail || err.message || message;
    } catch {
      // Ignore JSON parse errors, keep fallback message.
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

function toEngagementPayload(data) {
  return {
    contact_name: data.contactName || null,
    industry: data.industry || null,
    city: data.cityArea || null,
    phone: data.phone || null,
    email: data.email || null,
    website: data.website || null,
    gbp_account_id: data.gbpAccountId || null,
    gbp_location_id: data.gbpLocationId || null,
    gbp_access: data.gbpAccessStatus || null,
    start_type: data.startingPoint || null,
    current_rating: data.currentRating === '' ? null : Number(data.currentRating),
    review_count: data.currentReviewCount === '' ? null : Number(data.currentReviewCount),
    main_goal: data.topGoal || null,
    notes: data.notes || null,
  };
}

function fromEngagementPayload(data) {
  return {
    clientId: String(data.id),
    businessId: data.business_id == null ? '' : String(data.business_id),
    contactName: data.contact_name || '',
    industry: data.industry || '',
    cityArea: data.city || '',
    phone: data.phone || '',
    email: data.email || '',
    website: data.website || '',
    gbpAccountId: data.gbp_account_id || '',
    gbpLocationId: data.gbp_location_id || '',
    gbpAccessStatus: data.gbp_access || '',
    startingPoint: data.start_type || '',
    currentRating: data.current_rating == null ? '' : String(data.current_rating),
    currentReviewCount: data.review_count == null ? '' : String(data.review_count),
    topGoal: data.main_goal || '',
    notes: data.notes || '',
  };
}

async function fetchBusinessProfile(businessId) {
  if (!businessId) {
    return {
      businessName: '',
      email: '',
      phone: '',
      website: '',
    };
  }
  const business = await requestJson(`/businesses/${businessId}`, { method: 'GET' });
  return {
    businessName: business?.name || '',
    email: business?.email || '',
    phone: business?.phone || '',
    website: business?.website || '',
  };
}

async function updateBusinessProfile(businessId, form) {
  if (!businessId) return;

  const payload = {
    name: form.businessName?.trim() || null,
    email: form.email?.trim() || null,
    phone: form.phone?.trim() || null,
    website: form.website?.trim() || null,
  };

  await requestJson(`/businesses/${businessId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

function toAuditPayload(data) {
  return {
    auditor: data.auditedBy || null,
    date_delivered: data.dateDelivered || null,
    gbp_status: data.gbpStatus || null,
    gbp_photos: data.gbpPhotos || null,
    gbp_rating: data.starRating === '' ? null : Number(data.starRating),
    gbp_reviews: data.reviewCount === '' ? null : Number(data.reviewCount),
    rank_term_1: data.keyword1 || null,
    rank_position_1: data.position1 === '' ? null : Number(data.position1),
    rank_term_2: data.keyword2 || null,
    rank_position_2: data.position2 === '' ? null : Number(data.position2),
    website_score: data.websiteScore || null,
    citation_notes: data.citationConsistency || null,
    priority_issue_1: data.issue1 || null,
    priority_issue_2: data.issue2 || null,
    priority_issue_3: data.issue3 || null,
    quick_win_1: data.quickWin1 || null,
    quick_win_2: data.quickWin2 || null,
    notes: data.notes || null,
  };
}

function fromAuditPayload(data) {
  return {
    auditedBy: data.auditor || '',
    dateDelivered: data.date_delivered || '',
    gbpStatus: data.gbp_status || '',
    gbpPhotos: data.gbp_photos || '',
    starRating: data.gbp_rating == null ? '' : String(data.gbp_rating),
    reviewCount: data.gbp_reviews == null ? '' : String(data.gbp_reviews),
    websiteScore: data.website_score || '',
    citationConsistency: data.citation_notes || '',
    keyword1: data.rank_term_1 || '',
    position1: data.rank_position_1 == null ? '' : String(data.rank_position_1),
    keyword2: data.rank_term_2 || '',
    position2: data.rank_position_2 == null ? '' : String(data.rank_position_2),
    issue1: data.priority_issue_1 || '',
    issue2: data.priority_issue_2 || '',
    issue3: data.priority_issue_3 || '',
    quickWin1: data.quick_win_1 || '',
    quickWin2: data.quick_win_2 || '',
    notes: data.notes || '',
  };
}

function toMonthEndPayload(data) {
  return {
    period: data.reportPeriod || null,
    rank_term_1: data.keyword1 || null,
    rank_before_1: data.kw1Before === '' ? null : Number(data.kw1Before),
    rank_after_1: data.kw1After === '' ? null : Number(data.kw1After),
    rank_term_2: data.keyword2 || null,
    rank_before_2: data.kw2Before === '' ? null : Number(data.kw2Before),
    rank_after_2: data.kw2After === '' ? null : Number(data.kw2After),
    reviews_before: data.reviewsBefore === '' ? null : Number(data.reviewsBefore),
    reviews_after: data.reviewsAfter === '' ? null : Number(data.reviewsAfter),
    rating_before: data.ratingBefore === '' ? null : Number(data.ratingBefore),
    rating_after: data.ratingAfter === '' ? null : Number(data.ratingAfter),
    profile_views_before: data.viewsBefore === '' ? null : Number(data.viewsBefore),
    profile_views_after: data.viewsAfter === '' ? null : Number(data.viewsAfter),
    gbp_changes: data.changesMade || null,
    highlights: data.highlights || null,
    next_month_plan: data.month2Plan || null,
  };
}

function fromMonthEndPayload(data) {
  return {
    reportPeriod: data.period || '',
    keyword1: data.rank_term_1 || '',
    kw1Before: data.rank_before_1 == null ? '' : String(data.rank_before_1),
    kw1After: data.rank_after_1 == null ? '' : String(data.rank_after_1),
    keyword2: data.rank_term_2 || '',
    kw2Before: data.rank_before_2 == null ? '' : String(data.rank_before_2),
    kw2After: data.rank_after_2 == null ? '' : String(data.rank_after_2),
    reviewsBefore: data.reviews_before == null ? '' : String(data.reviews_before),
    reviewsAfter: data.reviews_after == null ? '' : String(data.reviews_after),
    ratingBefore: data.rating_before == null ? '' : String(data.rating_before),
    ratingAfter: data.rating_after == null ? '' : String(data.rating_after),
    viewsBefore: data.profile_views_before == null ? '' : String(data.profile_views_before),
    viewsAfter: data.profile_views_after == null ? '' : String(data.profile_views_after),
    changesMade: data.gbp_changes || '',
    highlights: data.highlights || '',
    month2Plan: data.next_month_plan || '',
  };
}

// POST /demo/engagements/new — creates Business + Engagement, returns engagement (ID auto-incremented)
export async function createNewEngagement(businessName = 'New Client') {
  const data = await requestJson('/demo/engagements/new', {
    method: 'POST',
    body: JSON.stringify({ business_name: businessName || 'New Client' }),
  });
  return { id: data.id, business_id: data.business_id, ...data };
}

// PATCH /demo/engagements/{engagementId}
export async function saveClientIntake(data) {
  const engagementId = resolveEngagementId(data.clientId || data.engagementId);
  if (!engagementId) throw new Error('Missing engagement ID. Set clientId or VITE_DEMO_ENGAGEMENT_ID.');

  const saved = await requestJson(`/demo/engagements/${engagementId}`, {
    method: 'PATCH',
    body: JSON.stringify(toEngagementPayload(data)),
  });

  try {
    await updateBusinessProfile(saved.business_id, data);
  } catch (error) {
    const detail = error?.message ? ` ${error.message}` : '';
    throw new Error(`Engagement saved, but business profile update failed.${detail}`.trim());
  }

  return {
    ...fromEngagementPayload(saved),
    businessName: data.businessName || '',
    email: data.email || '',
    phone: data.phone || '',
    website: data.website || '',
  };
}

// GET /demo/engagements/{engagementId}
export async function fetchClientIntake(clientId) {
  const engagementId = resolveEngagementId(clientId);
  if (!engagementId) return null;
  const data = await requestJson(`/demo/engagements/${engagementId}`);
  const businessProfile = await fetchBusinessProfile(data.business_id);
  return {
    ...fromEngagementPayload(data),
    ...businessProfile,
  };
}

// PUT /demo/engagements/{engagementId}/tasks/{taskId}
export async function saveTaskState(clientId, checkedMap) {
  const engagementId = resolveEngagementId(clientId);
  if (!engagementId) throw new Error('Missing engagement ID for task state persistence.');

  const entries = Object.entries(checkedMap || {});
  await Promise.all(
    entries.map(([taskId, completed]) =>
      requestJson(`/demo/engagements/${engagementId}/tasks/${encodeURIComponent(taskId)}`, {
        method: 'PUT',
        body: JSON.stringify({ completed: !!completed }),
      }),
    ),
  );
  return { ok: true };
}

// GET /demo/engagements/{engagementId}/tasks
export async function fetchTaskState(clientId) {
  const engagementId = resolveEngagementId(clientId);
  if (!engagementId) return {};
  const rows = await requestJson(`/demo/engagements/${engagementId}/tasks`);
  return rows.reduce((acc, row) => {
    acc[row.task_id] = !!row.completed;
    return acc;
  }, {});
}

// GET /demo/engagements/{engagementId}/reviews
export async function fetchReviews(engagementId) {
  const id = resolveEngagementId(engagementId);
  if (!id) return { total: 0, unanswered_count: 0, reviews: [] };
  const reviews = await requestJson(`/demo/engagements/${id}/reviews`);
  return {
    total: reviews.length,
    unanswered_count: reviews.filter((r) => !r.has_reply).length,
    reviews,
  };
}

// POST /demo/engagements/{engagementId}/reviews/auto-reply
export async function triggerAutoReply(engagementId, _locationId, options = {}) {
  const id = resolveEngagementId(engagementId);
  if (!id) throw new Error('Missing engagement ID for auto-reply.');
  return requestJson(`/demo/engagements/${id}/reviews/auto-reply`, {
    method: 'POST',
    body: JSON.stringify({
      tone: options.tone || 'warm',
      dry_run: options.dry_run !== false,
    }),
  });
}

// POST /demo/engagements/{engagementId}/reviews/{reviewId}/reply
export async function generateSingleReply(payload) {
  const engagementId = resolveEngagementId(payload.engagementId || payload.clientId);
  if (!engagementId || !payload.reviewId) {
    throw new Error('Missing engagementId or reviewId for single reply generation.');
  }

  const result = await requestJson(`/demo/engagements/${engagementId}/reviews/${payload.reviewId}/reply`, {
    method: 'POST',
    body: JSON.stringify({
      tone: payload.tone || 'warm',
      dry_run: payload.dry_run !== false,
    }),
  });
  return { reply: result.reply };
}

// GET /demo/engagements/{engagementId}/audit
export async function fetchAuditReport(clientId) {
  const engagementId = resolveEngagementId(clientId);
  if (!engagementId) return null;
  try {
    const data = await requestJson(`/demo/engagements/${engagementId}/audit`);
    return fromAuditPayload(data);
  } catch (error) {
    if (String(error.message).toLowerCase().includes('not found')) return null;
    throw error;
  }
}

// POST/PATCH /demo/engagements/{engagementId}/audit
export async function saveAuditReport(clientId, form) {
  const engagementId = resolveEngagementId(clientId);
  if (!engagementId) throw new Error('Missing engagement ID for audit persistence.');
  const payload = toAuditPayload(form);
  try {
    const created = await requestJson(`/demo/engagements/${engagementId}/audit`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    return fromAuditPayload(created);
  } catch (error) {
    if (!String(error.message).toLowerCase().includes('already exists')) throw error;
    const updated = await requestJson(`/demo/engagements/${engagementId}/audit`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
    return fromAuditPayload(updated);
  }
}

// GET /demo/engagements/{engagementId}/month-end
export async function fetchMonthEndReport(clientId) {
  const engagementId = resolveEngagementId(clientId);
  if (!engagementId) return null;
  try {
    const data = await requestJson(`/demo/engagements/${engagementId}/month-end`);
    return fromMonthEndPayload(data);
  } catch (error) {
    if (String(error.message).toLowerCase().includes('not found')) return null;
    throw error;
  }
}

// POST/PATCH /demo/engagements/{engagementId}/month-end
export async function saveMonthEndReport(clientId, form) {
  const engagementId = resolveEngagementId(clientId);
  if (!engagementId) throw new Error('Missing engagement ID for month-end persistence.');
  const payload = toMonthEndPayload(form);
  try {
    const created = await requestJson(`/demo/engagements/${engagementId}/month-end`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    return fromMonthEndPayload(created);
  } catch (error) {
    if (!String(error.message).toLowerCase().includes('already exists')) throw error;
    const updated = await requestJson(`/demo/engagements/${engagementId}/month-end`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
    return fromMonthEndPayload(updated);
  }
}
