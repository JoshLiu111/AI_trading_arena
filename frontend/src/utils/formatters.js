/**
 * Unified formatting utilities
 * Eliminates repeated formatting code across components
 */

// ==================== Currency Formatting ====================

/**
 * Format number as currency (USD)
 * @param {number} value - The number to format
 * @param {object} options - Formatting options
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (value, options = {}) => {
  const {
    showSign = false,      // Show +/- sign
    decimals = 2,          // Decimal places
    fallback = "N/A",      // Fallback for invalid values
  } = options;

  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }

  const formatted = Math.abs(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  if (showSign && value !== 0) {
    return value >= 0 ? `+$${formatted}` : `-$${formatted}`;
  }

  return `$${formatted}`;
};

/**
 * Format number with locale settings (no currency symbol)
 * @param {number} value - The number to format
 * @param {number} decimals - Decimal places
 * @returns {string} Formatted number string
 */
export const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined || isNaN(value)) {
    return "N/A";
  }

  return value.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

// ==================== Percentage Formatting ====================

/**
 * Format number as percentage
 * @param {number} value - The percentage value
 * @param {object} options - Formatting options
 * @returns {string} Formatted percentage string
 */
export const formatPercent = (value, options = {}) => {
  const {
    showSign = true,
    decimals = 2,
    fallback = "0.00%",
  } = options;

  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }

  const formatted = Math.abs(value).toFixed(decimals);
  
  if (showSign && value !== 0) {
    return value >= 0 ? `+${formatted}%` : `-${formatted}%`;
  }

  return `${formatted}%`;
};

// ==================== Date/Time Formatting ====================

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @param {object} options - Formatting options
 * @returns {string} Formatted date string
 */
export const formatDate = (date, options = {}) => {
  const { includeTime = false, fallback = "N/A" } = options;

  if (!date) return fallback;

  try {
    const dateObj = new Date(date);
    
    if (includeTime) {
      return dateObj.toLocaleString();
    }
    
    return dateObj.toLocaleDateString();
  } catch {
    return fallback;
  }
};

// ==================== P&L Formatting ====================

/**
 * Format profit/loss with percentage and amount
 * @param {number} currentValue - Current value
 * @param {number} initialValue - Initial/cost value
 * @returns {object} Formatted P&L data
 */
export const formatPnL = (currentValue, initialValue) => {
  if (!currentValue || !initialValue || initialValue === 0) {
    return {
      amount: 0,
      percent: 0,
      formatted: "$0.00 (0.00%)",
      isPositive: true,
    };
  }

  const amount = currentValue - initialValue;
  const percent = (amount / initialValue) * 100;
  const isPositive = amount >= 0;

  const sign = isPositive ? "+" : "";
  const formatted = `${sign}${formatPercent(percent, { showSign: false })} (${formatCurrency(amount, { showSign: true })})`;

  return {
    amount,
    percent,
    formatted,
    isPositive,
  };
};

// ==================== Quantity/Shares Formatting ====================

/**
 * Format share quantity with label
 * @param {number} quantity - Number of shares
 * @returns {string} Formatted shares string
 */
export const formatShares = (quantity) => {
  if (!quantity || quantity === 0) return "0 shares";
  return `${quantity} share${quantity !== 1 ? "s" : ""}`;
};

// ==================== CSS Class Helpers ====================

/**
 * Get CSS class based on positive/negative value
 * @param {number|boolean} value - Value or isPositive boolean
 * @returns {string} CSS class name
 */
export const getPnLClass = (value) => {
  if (typeof value === "boolean") {
    return value ? "positive" : "negative";
  }
  return value >= 0 ? "positive" : "negative";
};
