/**
 * Trading API
 */
import { fetchAPI } from "./fetchAPI";

// POST /api/v1/trading/execute - Human player trade execution
export async function executeTrade(tradeData) {
  return fetchAPI("/trading/execute", {
    method: "POST",
    body: tradeData,
  });
}

// GET /api/v1/trading/strategy/{account_id} - Get latest AI strategy for account
export async function getLatestStrategy(accountId) {
  return fetchAPI(`/trading/strategy/${accountId}`);
}

// GET /api/v1/trading/strategies/{account_id} - Get strategy history for account
export async function getStrategyHistory(accountId) {
  return fetchAPI(`/trading/strategies/${accountId}`);
}

