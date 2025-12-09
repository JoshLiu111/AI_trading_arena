/**
 * Application constants
 * Eliminates magic strings throughout the codebase
 */

// Account types
export const ACCOUNT_TYPES = {
  HUMAN: "human",
  AI: "ai",
};

// Trade actions
export const TRADE_ACTIONS = {
  BUY: "BUY",
  SELL: "SELL",
};

// Sort options
export const SORT_OPTIONS = {
  PRICE_DESC: "price_desc",
  PRICE_ASC: "price_asc",
  CHANGE_DESC: "change_desc",
  CHANGE_ASC: "change_asc",
};

export const SORT_LABELS = {
  [SORT_OPTIONS.PRICE_DESC]: "Price (High To Low)",
  [SORT_OPTIONS.PRICE_ASC]: "Price (Low To High)",
  [SORT_OPTIONS.CHANGE_DESC]: "24h Change (High To Low)",
  [SORT_OPTIONS.CHANGE_ASC]: "24h Change (Low To High)",
};

// Competition status
export const COMPETITION_STATUS = {
  RUNNING: "running",
  PAUSED: "paused",
  STOPPED: "stopped",
};

// API defaults
export const API_DEFAULTS = {
  HISTORY_DAYS: 7,
  DEFAULT_AI_ACCOUNT_ID: 2,
};

// Routes
export const ROUTES = {
  HOME: "/",
  DASHBOARD: "/dashboard",
  STOCK_DETAIL: "/stock/:ticker",
  ACCOUNT_DETAIL: "/account/:accountId",
  LEARN_MORE: "/learn-more",
};

// Chart colors (from CSS variables)
export const CHART_COLORS = {
  PRIMARY: "rgb(59, 130, 246)",    // --accent-blue
  SECONDARY: "rgb(139, 92, 246)",  // --accent-purple
  GREEN: "rgb(16, 185, 129)",      // --green
  RED: "rgb(239, 68, 68)",         // --red
  TEXT: "#9CA3AF",                 // --text-secondary
  GRID: "rgba(156, 163, 175, 0.1)",
};
