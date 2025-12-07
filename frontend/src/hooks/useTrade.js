import { useState, useCallback } from "react";
import { executeTrade } from "../services/api";

/**
 * Custom hook for handling trade operations
 * Extracts trading logic from StockDetail component
 */
export const useTrade = (ticker, humanAccountId, stock) => {
  // Form state
  const [tradeAction, setTradeAction] = useState("BUY");
  const [tradeQuantity, setTradeQuantity] = useState(1);
  const [tradeRationale, setTradeRationale] = useState("");
  
  // Operation state
  const [trading, setTrading] = useState(false);
  const [tradeSuccess, setTradeSuccess] = useState(null);
  const [tradeError, setTradeError] = useState(null);

  /**
   * Validate trade before execution
   */
  const validateTrade = useCallback((accountBalance, accountPositions) => {
    if (!humanAccountId || !tradeQuantity || tradeQuantity <= 0) {
      return { valid: false, error: "Human account not found or invalid quantity" };
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
  }, [humanAccountId, tradeQuantity, tradeAction, stock, ticker]);

  /**
   * Execute the trade
   */
  const handleTrade = useCallback(async (accountBalance, accountPositions, onSuccess) => {
    // Validate first
    const validation = validateTrade(accountBalance, accountPositions);
    if (!validation.valid) {
      setTradeError(validation.error);
      return { success: false };
    }

    try {
      setTrading(true);
      setTradeError(null);
      setTradeSuccess(null);

      const tradeData = {
        account_id: humanAccountId,
        ticker: ticker.toUpperCase(),
        action: tradeAction,
        quantity: parseInt(tradeQuantity),
        rationale: tradeRationale || null,
      };

      await executeTrade(tradeData);

      setTradeSuccess(
        `Trade executed successfully! ${tradeAction} ${tradeQuantity} shares of ${ticker.toUpperCase()}`
      );

      // Reset form
      setTradeQuantity(1);
      setTradeRationale("");

      // Call success callback if provided
      if (onSuccess) {
        await onSuccess();
      }

      return { success: true };
    } catch (err) {
      setTradeError(err.message || "Failed to execute trade");
      console.error("Error executing trade:", err);
      return { success: false };
    } finally {
      setTrading(false);
    }
  }, [humanAccountId, ticker, tradeAction, tradeQuantity, tradeRationale, validateTrade]);

  /**
   * Reset trade form and messages
   */
  const resetTrade = useCallback(() => {
    setTradeAction("BUY");
    setTradeQuantity(1);
    setTradeRationale("");
    setTradeSuccess(null);
    setTradeError(null);
  }, []);

  /**
   * Clear messages only
   */
  const clearMessages = useCallback(() => {
    setTradeSuccess(null);
    setTradeError(null);
  }, []);

  // Calculate total cost
  const totalCost = stock?.current_price ? stock.current_price * tradeQuantity : 0;

  return {
    // Form state
    tradeAction,
    setTradeAction,
    tradeQuantity,
    setTradeQuantity,
    tradeRationale,
    setTradeRationale,
    
    // Operation state
    trading,
    tradeSuccess,
    tradeError,
    
    // Computed values
    totalCost,
    
    // Actions
    handleTrade,
    validateTrade,
    resetTrade,
    clearMessages,
  };
};

export default useTrade;
