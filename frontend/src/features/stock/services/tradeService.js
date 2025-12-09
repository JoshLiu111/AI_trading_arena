/**
 * Trade Service
 * Business logic for trade operations (validation, execution)
 */

import { executeTrade } from "@/lib/api";

/**
 * Validate trade before execution
 */
export function validateTrade(tradeAction, tradeQuantity, stock, accountBalance, accountPositions, ticker) {
  if (!tradeQuantity || tradeQuantity <= 0) {
    return { valid: false, error: "Invalid quantity" };
  }

  if (!stock?.current_price || stock.current_price <= 0) {
    return { valid: false, error: "Invalid stock price" };
  }

  const totalCost = stock.current_price * tradeQuantity;
  const currentTicker = ticker.toUpperCase();

  // BUY validation
  if (tradeAction === "BUY") {
    if (accountBalance <= 0) {
      return { valid: false, error: "Insufficient balance. Your account balance is $0.00" };
    }
    if (accountBalance < totalCost) {
      return { 
        valid: false, 
        error: `Insufficient balance. You have $${accountBalance.toFixed(2)}, but need $${totalCost.toFixed(2)}` 
      };
    }
  }

  // SELL validation
  if (tradeAction === "SELL") {
    const position = accountPositions[currentTicker];
    const currentQuantity = position?.quantity || 0;

    if (currentQuantity <= 0) {
      return { valid: false, error: `You don't own any shares of ${currentTicker}. Cannot sell.` };
    }
    if (currentQuantity < tradeQuantity) {
      return { 
        valid: false, 
        error: `Insufficient shares. You own ${currentQuantity} shares, but trying to sell ${tradeQuantity} shares.` 
      };
    }
  }

  return { valid: true, error: null };
}

/**
 * Execute trade
 */
export async function executeTradeService(tradeData) {
  try {
    await executeTrade(tradeData);
    return { 
      success: true, 
      message: `Trade executed successfully! ${tradeData.action} ${tradeData.quantity} shares of ${tradeData.ticker}`
    };
  } catch (err) {
    const errorMessage = err.message || "Failed to execute trade";
    console.error("Error executing trade:", err);
    return { success: false, error: errorMessage };
  }
}

