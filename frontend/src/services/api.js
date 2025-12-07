import {
  mockStocks,
  mockAccounts,
  getMockStockHistory,
  mockCompetitionStatus,
  getMockCompetitionStatus,
  mockStartCompetition,
  mockGenerateStrategy,
  mockRegenerateStrategy,
  mockPauseCompetition,
  mockResumeCompetition,
  mockExecuteTrade,
  getMockLatestStrategy,
  getMockStrategyHistory,
  getMockAccountById,
  getMockAccountTransactions,
  getMockAccountPositions,
} from "./mockData/index.js";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_VERSION = "/api/v1";

// 使用模拟数据模式（默认 false，连接真实后端）
// 设置为 true 或设置环境变量 VITE_USE_MOCK_DATA=true 来使用模拟数据
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === "true";

async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${API_VERSION}${endpoint}`;
  const defaultOptions = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {}),
    },
  };

  if (config.body && typeof config.body === "object") {
    config.body = JSON.stringify(config.body);
  }

  // Add timeout for long-running requests (like start_competition)
  const timeout = options.timeout || 300000; // 5 minutes default, 5 minutes for start_competition
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  config.signal = controller.signal;

  try {
    const response = await fetch(url, config);
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.message || errorJson.detail || errorMessage;
      } catch {
        errorMessage = errorText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout / 1000} seconds. The server may be processing a long-running operation.`);
    }
    console.error("API request failed:", error);
    throw error;
  }
}

// ==================== Accounts API ====================
// GET /api/v1/accounts - Get all accounts
export async function getAllAccounts() {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return mockAccounts;
  }
  const data = await fetchAPI("/accounts");
  return data.accounts || data;
}

// GET /api/v1/accounts/{id} - Get account details
export async function getAccountById(accountId) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return getMockAccountById(accountId);
  }
  return fetchAPI(`/accounts/${accountId}`);
}

// GET /api/v1/accounts/{id}/transactions - Get transaction history
export async function getAccountTransactions(accountId) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return getMockAccountTransactions(accountId);
  }
  return fetchAPI(`/accounts/${accountId}/transactions`);
}

// GET /api/v1/accounts/{id}/positions - Get current positions
export async function getAccountPositions(accountId) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return getMockAccountPositions(accountId);
  }
  return fetchAPI(`/accounts/${accountId}/positions`);
}

// ==================== Stocks API ====================
// GET /api/v1/stocks/prices - Get real-time prices for stocks
// Simplified logic: current_price = yfinance real-time price, or latest history close if unavailable
export async function getStockPrices() {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return mockStocks;
  }
  const data = await fetchAPI("/stocks/prices");
  const stocks = data.stocks || data;
  
  // For each stock, if yfinance price is not available, fetch from history data
  const stocksWithPrice = await Promise.all(
    stocks.map(async (stock) => {
      let currentPrice = stock.price !== null && stock.price !== undefined ? stock.price : stock.current_price;
      
      // If no real-time price, get latest close from history
      if (!currentPrice) {
        try {
          const historyData = await fetchAPI(`/stocks/${stock.ticker}/history?days=1`);
          if (historyData.data && historyData.data.length > 0) {
            // Use the latest close price
            currentPrice = historyData.data[historyData.data.length - 1]?.close || null;
          }
        } catch (err) {
          console.warn(`Failed to get price for ${stock.ticker}:`, err);
        }
      }
      
      return {
        ticker: stock.ticker,
        name: stock.name || stock.ticker,
        current_price: currentPrice,
        open: stock.open,
        high: stock.high,
        low: stock.low,
        volume: stock.volume,
        updated_at: stock.updated_at,
        ...(stock.description && { description: stock.description }),
      };
    })
  );
  
  return stocksWithPrice;
}

// GET /api/v1/stocks/{ticker}/history - Get historical K-line data
export async function getStockHistory(ticker, params = {}) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return getMockStockHistory(ticker, params);
  }
  const queryString = new URLSearchParams(params).toString();
  const endpoint = `/stocks/${ticker}/history${
    queryString ? `?${queryString}` : ""
  }`;
  const historyData = await fetchAPI(endpoint);
  
  return {
    ticker: historyData.ticker || ticker,
    data: historyData.data || [],
  };
}

// ==================== Competition API ====================
// POST /api/v1/competition/start - Start competition (full reset + set is_running=true)
export async function startCompetition(competitionData = {}) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return mockStartCompetition();
  }
  // Start competition can take a long time (refresh data, generate AI strategy)
  return fetchAPI("/competition/start", {
    method: "POST",
    body: competitionData,
    timeout: 300000, // 5 minutes timeout
  });
}

// POST /api/v1/competition/generate-strategy - Generate strategy only (no reset)
export async function generateStrategy(accountId = null) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    return mockGenerateStrategy();
  }
  const params = accountId ? `?account_id=${accountId}` : "";
  return fetchAPI(`/competition/generate-strategy${params}`, {
    method: "POST",
    timeout: 120000, // 2 minutes timeout
  });
}

// POST /api/v1/competition/regenerate-strategy - Delete and regenerate strategy
export async function regenerateStrategy(accountId = null) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    return mockRegenerateStrategy();
  }
  const params = accountId ? `?account_id=${accountId}` : "";
  return fetchAPI(`/competition/regenerate-strategy${params}`, {
    method: "POST",
    timeout: 120000, // 2 minutes timeout
  });
}

// POST /api/v1/competition/pause - Pause trading
export async function pauseCompetition() {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return mockPauseCompetition();
  }
  return fetchAPI("/competition/pause", { method: "POST" });
}

// POST /api/v1/competition/resume - Resume trading
export async function resumeCompetition() {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return mockResumeCompetition();
  }
  return fetchAPI("/competition/resume", { method: "POST" });
}

// GET /api/v1/competition/status - Get competition status
export async function getCompetitionStatus() {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return getMockCompetitionStatus();
  }
  return fetchAPI("/competition/status");
}

// ==================== Trading API ====================
// POST /api/v1/trading/execute - Human player trade execution
export async function executeTrade(tradeData) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return mockExecuteTrade(tradeData);
  }
  return fetchAPI("/trading/execute", {
    method: "POST",
    body: tradeData,
  });
}

// GET /api/v1/trading/strategy/{account_id} - Get latest AI strategy for account
export async function getLatestStrategy(accountId) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return getMockLatestStrategy(accountId);
  }
  return fetchAPI(`/trading/strategy/${accountId}`);
}

// GET /api/v1/trading/strategies/{account_id} - Get strategy history for account
export async function getStrategyHistory(accountId) {
  if (USE_MOCK_DATA) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return getMockStrategyHistory(accountId);
  }
  return fetchAPI(`/trading/strategies/${accountId}`);
}
