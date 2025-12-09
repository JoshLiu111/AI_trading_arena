import { useState } from "react";
import * as tradeService from "../services/tradeService";

/**
 * Custom hook for trade operations
 * @param {object} options - Trade configuration
 * @param {string} options.ticker - Stock ticker
 * @param {object} options.stock - Stock data
 * @param {number} options.accountId - Account ID for the trade
 * @param {number} options.accountBalance - Account balance
 * @param {object} options.accountPositions - Account positions
 * @param {function} options.onSuccess - Callback on successful trade
 * @returns {object} Trade state and handlers
 */
export function useTrade({ ticker, stock, accountId, accountBalance, accountPositions, onSuccess }) {
  const [tradeAction, setTradeAction] = useState("BUY");
  // tradeQuantity can be number or string (for user input)
  const [tradeQuantity, setTradeQuantity] = useState(1);
  const [tradeRationale, setTradeRationale] = useState("");
  const [trading, setTrading] = useState(false);
  const [tradeSuccess, setTradeSuccess] = useState(null);
  const [tradeError, setTradeError] = useState(null);

  const handleTradeSubmit = async (e) => {
    e.preventDefault();
    
    if (!ticker || !stock) {
      setTradeError("Stock information is missing");
      return;
    }

    if (!accountId) {
      setTradeError("Account ID is missing");
      return;
    }

    // Validate and parse quantity (handle both number and string)
    const quantityValue = typeof tradeQuantity === "string" ? tradeQuantity.trim() : String(tradeQuantity);
    const parsedQuantity = parseInt(quantityValue, 10);
    if (isNaN(parsedQuantity) || parsedQuantity <= 0) {
      setTradeError("Invalid quantity. Please enter a positive number.");
      return;
    }

    // Validate trade
    const validation = tradeService.validateTrade(
      tradeAction,
      parsedQuantity,
      stock,
      accountBalance,
      accountPositions,
      ticker
    );
    
    if (!validation.valid) {
      setTradeError(validation.error);
      return;
    }

    try {
      setTrading(true);
      setTradeError(null);
      setTradeSuccess(null);

      const tradeData = {
        account_id: accountId,
        ticker: ticker.toUpperCase(),
        action: tradeAction,
        quantity: parsedQuantity,
        rationale: tradeRationale || null,
      };

      const result = await tradeService.executeTradeService(tradeData);

      if (result.success) {
        setTradeSuccess(result.message);
        // Reset form
        setTradeQuantity(1);
        setTradeRationale("");
        // Call success callback if provided
        if (onSuccess) {
          onSuccess();
        }
      } else {
        setTradeError(result.error);
      }
    } catch (err) {
      setTradeError(err.message || "Failed to execute trade");
      console.error("Error executing trade:", err);
    } finally {
      setTrading(false);
    }
  };

  // Calculate total cost (handle both number and string for tradeQuantity)
  const quantityForCalculation = typeof tradeQuantity === "number" 
    ? tradeQuantity 
    : (parseInt(tradeQuantity, 10) || 0);
  const totalCost = stock?.current_price ? stock.current_price * quantityForCalculation : 0;

  return {
    // Trade form state
    tradeAction,
    setTradeAction,
    tradeQuantity,
    setTradeQuantity, // Allow both number and string for user input
    tradeRationale,
    setTradeRationale,
    totalCost,
    // Operation state
    trading,
    tradeSuccess,
    tradeError,
    // Handlers
    handleTradeSubmit,
  };
}

