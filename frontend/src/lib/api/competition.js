/**
 * Competition API
 */
import { fetchAPI } from "./fetchAPI";

// POST /api/v1/competition/start - Start competition (full reset + set is_running=true)
export async function startCompetition(competitionData = {}) {
  // Start competition can take a long time (refresh data, generate AI strategy)
  return fetchAPI("/competition/start", {
    method: "POST",
    body: competitionData,
    timeout: 300000, // 5 minutes timeout
  });
}

// POST /api/v1/competition/generate-strategy - Generate strategy only (no reset)
export async function generateStrategy(accountId = null) {
  const params = accountId ? `?account_id=${accountId}` : "";
  return fetchAPI(`/competition/generate-strategy${params}`, {
    method: "POST",
    timeout: 120000, // 2 minutes timeout
  });
}

// POST /api/v1/competition/regenerate-strategy - Delete and regenerate strategy
export async function regenerateStrategy(accountId = null) {
  const params = accountId ? `?account_id=${accountId}` : "";
  return fetchAPI(`/competition/regenerate-strategy${params}`, {
    method: "POST",
    timeout: 120000, // 2 minutes timeout
  });
}

// POST /api/v1/competition/pause - Pause trading
export async function pauseCompetition() {
  return fetchAPI("/competition/pause", { method: "POST" });
}

// POST /api/v1/competition/resume - Resume trading
export async function resumeCompetition() {
  return fetchAPI("/competition/resume", { method: "POST" });
}

// GET /api/v1/competition/status - Get competition status
export async function getCompetitionStatus() {
  return fetchAPI("/competition/status");
}

