/**
 * @fileoverview Centralised backend communication layer for the Demo Toolkit.
 * All functions are currently stubs returning mock data. When a real backend is
 * connected, only this file needs to change — no component logic changes.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// POST /clients/{clientId}/intake
export async function saveClientIntake(data) {
  return { ok: true };
}

// GET /clients/{clientId}/intake
export async function fetchClientIntake(clientId) {
  return null;
}

// PUT /clients/{clientId}/tasks
export async function saveTaskState(clientId, checkedMap) {
  return { ok: true };
}

// GET /clients/{clientId}/tasks
export async function fetchTaskState(clientId) {
  return {};
}

// GET /reviews/{accountId}/{locationId}
export async function fetchReviews(accountId, locationId) {
  return { total: 0, unanswered_count: 0, reviews: [] };
}

// POST /reviews/{accountId}/{locationId}/auto-reply
export async function triggerAutoReply(accountId, locationId, options) {
  return { processed: 0, succeeded: 0, failed: 0, dry_run: true, results: [] };
}

// POST /reviews/generate-reply
export async function generateSingleReply(payload) {
  return { reply: 'Thank you for your review...' };
}
