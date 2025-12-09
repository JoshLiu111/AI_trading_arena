/**
 * Accounts API
 */
import { fetchAPI } from "./fetchAPI";

// GET /api/v1/accounts/ - Get all accounts
export async function getAllAccounts() {
  const data = await fetchAPI("/accounts/"); // Add trailing slash to avoid 307 redirect
  return data.accounts || data;
}

// GET /api/v1/accounts/{id} - Get account details
export async function getAccountById(accountId) {
  return fetchAPI(`/accounts/${accountId}`);
}

// GET /api/v1/accounts/{id}/transactions - Get transaction history
export async function getAccountTransactions(accountId) {
  return fetchAPI(`/accounts/${accountId}/transactions`);
}

// GET /api/v1/accounts/{id}/positions - Get current positions
export async function getAccountPositions(accountId) {
  return fetchAPI(`/accounts/${accountId}/positions`);
}

