/**
 * Mock data for development/testing
 * These functions return placeholder data when USE_MOCK_DATA is true
 */

// Stock pool (matching backend config)
const STOCK_POOL = [
  "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
  "META", "TSLA", "JPM", "V", "WMT"
];

// Generate mock stock data
const generateMockStock = (ticker) => {
  const basePrice = 100 + Math.random() * 200; // Random price between 100-300
  const changePercent = (Math.random() - 0.5) * 10; // Random change between -5% to +5%
  const previousClose = basePrice / (1 + changePercent / 100);
  
  return {
    ticker,
    name: getStockName(ticker),
    current_price: basePrice,
    previous_close: previousClose,
    open: basePrice * (1 + (Math.random() - 0.5) * 0.02),
    high: basePrice * (1 + Math.random() * 0.05),
    low: basePrice * (1 - Math.random() * 0.05),
    volume: Math.floor(Math.random() * 10000000) + 1000000,
    updated_at: new Date().toISOString(),
  };
};

const getStockName = (ticker) => {
  const names = {
    AAPL: "Apple Inc.",
    MSFT: "Microsoft Corporation",
    GOOGL: "Alphabet Inc.",
    AMZN: "Amazon.com Inc.",
    NVDA: "NVIDIA Corporation",
    META: "Meta Platforms Inc.",
    TSLA: "Tesla Inc.",
    JPM: "JPMorgan Chase & Co.",
    V: "Visa Inc.",
    WMT: "Walmart Inc.",
  };
  return names[ticker] || ticker;
};

// Mock stocks data
export const mockStocks = STOCK_POOL.map(ticker => generateMockStock(ticker));

// Mock accounts data
export const mockAccounts = [
  {
    id: 1,
    account_name: "human_player",
    display_name: "Human Player",
    account_type: "human",
    balance: 1000000.00,
    initial_balance: 1000000.00,
    total_value: 1000000.00,
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    account_name: "openai_player",
    display_name: "OpenAI Player",
    account_type: "ai",
    balance: 1000000.00,
    initial_balance: 1000000.00,
    total_value: 1000000.00,
    created_at: new Date().toISOString(),
  },
];

// Mock stock history
export const getMockStockHistory = async (ticker, params = {}) => {
  const days = params.days || 7;
  const basePrice = 100 + Math.random() * 200;
  const data = [];
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const priceVariation = (Math.random() - 0.5) * 0.1; // ±5% variation
    const close = basePrice * (1 + priceVariation);
    
    data.push({
      date: date.toISOString().split('T')[0],
      open: close * (1 + (Math.random() - 0.5) * 0.02),
      high: close * (1 + Math.random() * 0.03),
      low: close * (1 - Math.random() * 0.03),
      close: close,
      volume: Math.floor(Math.random() * 10000000) + 1000000,
      adj_close: close,
    });
  }
  
  return { ticker, data };
};

// Mock competition status (shared state)
let mockCompetitionState = {
  is_running: false,
  is_paused: false,
  started_at: null,
  last_trade_at: null,
};

// Mock competition status getter
export const mockCompetitionStatus = {
  get is_running() {
    return mockCompetitionState.is_running;
  },
  get is_paused() {
    return mockCompetitionState.is_paused;
  },
  get started_at() {
    return mockCompetitionState.started_at;
  },
  get last_trade_at() {
    return mockCompetitionState.last_trade_at;
  },
};

// Mock competition actions
export const mockStartCompetition = async () => {
  // Update state
  mockCompetitionState = {
    is_running: true,
    is_paused: false,
    started_at: new Date().toISOString(),
    last_trade_at: null,
  };
  // Reset strategy state when starting competition
  mockStrategyState = null;
  return { 
    success: true, 
    message: "Competition started (mock)",
    accounts: mockAccounts,
  };
};

export const mockGenerateStrategy = async () => {
  // Generate mock strategy without resetting state
  mockStrategyState = {
    account_id: 2,
    content: {
      strategy: "Mock Trading Strategy",
      selected_stocks: ["AAPL", "MSFT", "GOOGL"],
      reasoning: "Mock strategy for testing",
      actions: [
        { ticker: "AAPL", action: "BUY", quantity: 10, rationale: "Strong fundamentals" },
        { ticker: "MSFT", action: "BUY", quantity: 5, rationale: "Cloud growth" },
      ],
    },
    strategy_content: JSON.stringify({
      strategy: "Mock Trading Strategy",
      selected_stocks: ["AAPL", "MSFT", "GOOGL"],
    }),
    selected_stocks: "AAPL,MSFT,GOOGL",
  };
  return { success: true, message: "Strategy generated (mock)", strategies_created: 1 };
};

export const mockRegenerateStrategy = async () => {
  // Delete and regenerate strategy
  mockStrategyState = null;
  // Generate new strategy
  return mockGenerateStrategy();
};

export const mockPauseCompetition = async () => {
  if (mockCompetitionState.is_running) {
    mockCompetitionState.is_paused = true;
  }
  return { success: true, message: "Competition paused (mock)" };
};

export const mockResumeCompetition = async () => {
  if (mockCompetitionState.is_running) {
    mockCompetitionState.is_paused = false;
  }
  return { success: true, message: "Competition resumed (mock)" };
};

// Export getter function for competition status
export const getMockCompetitionStatus = () => {
  return {
    is_running: mockCompetitionState.is_running,
    is_paused: mockCompetitionState.is_paused,
    started_at: mockCompetitionState.started_at,
    last_trade_at: mockCompetitionState.last_trade_at,
  };
};

// Mock trade execution
export const mockExecuteTrade = async (tradeData) => {
  return { success: true, message: "Trade executed (mock)", ...tradeData };
};

// Mock strategy functions
// Store mock strategy state
let mockStrategyState = null;

export const getMockLatestStrategy = async (accountId) => {
  // If competition is running, return a mock strategy
  if (mockCompetitionState.is_running && accountId === 2) {
    if (!mockStrategyState) {
      // Generate a mock strategy
      mockStrategyState = {
        account_id: accountId,
        content: {
          strategy: "Mock Trading Strategy",
          selected_stocks: ["AAPL", "MSFT", "GOOGL"],
          reasoning: "Mock strategy for testing",
          actions: [
            { ticker: "AAPL", action: "BUY", quantity: 10, rationale: "Strong fundamentals" },
            { ticker: "MSFT", action: "BUY", quantity: 5, rationale: "Cloud growth" },
          ],
        },
        strategy_content: JSON.stringify({
          strategy: "Mock Trading Strategy",
          selected_stocks: ["AAPL", "MSFT", "GOOGL"],
        }),
        selected_stocks: "AAPL,MSFT,GOOGL",
      };
    }
    return mockStrategyState;
  }
  // Return null if competition not running or no strategy
  return { account_id: accountId, strategy: null, content: null };
};

export const getMockStrategyHistory = async (accountId) => {
  return { account_id: accountId, strategies: [] };
};

// Mock account functions
export const getMockAccountById = async (accountId) => {
  // Return account matching the ID from mockAccounts
  const account = mockAccounts.find(acc => acc.id === accountId);
  if (account) {
    return {
      ...account,
      created_at: account.created_at || new Date().toISOString(),
    };
  }
  // Fallback if account not found
  return {
    id: accountId,
    account_name: accountId === 1 ? "human_player" : "openai_player",
    display_name: accountId === 1 ? "Human Player" : "OpenAI Player",
    account_type: accountId === 1 ? "human" : "ai",
    balance: 1000000,
    initial_balance: 1000000,
    total_value: 1000000,
    created_at: new Date().toISOString(),
  };
};

export const getMockAccountTransactions = async (accountId) => {
  // Return empty array or some mock transactions
  return [];
};

export const getMockAccountPositions = async (accountId) => {
  // Return positions in the same format as backend
  // Backend returns: { account_id, balance, positions: {...}, total_value }
  // positions is an object with ticker as key
  return {
    account_id: accountId,
    balance: 1000000,
    positions: {}, // Empty positions object (can be populated with mock data if needed)
    total_value: 1000000,
  };
};

