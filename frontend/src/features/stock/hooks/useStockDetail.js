import { useState, useEffect, useCallback } from "react";
import * as stockDetailService from "../services/stockDetailService";

/**
 * Custom hook for fetching stock detail data
 * @param {string} ticker - The stock ticker symbol
 * @returns {object} Stock data, history, accounts, and related account info
 */
export function useStockDetail(ticker) {
  const [stock, setStock] = useState(null);
  const [history, setHistory] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [humanAccountId, setHumanAccountId] = useState(null);
  const [accountBalance, setAccountBalance] = useState(0);
  const [accountPositions, setAccountPositions] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!ticker) {
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const data = await stockDetailService.fetchStockDetailData(ticker);
      
      setStock(data.stock);
      setHistory(data.history);
      setAccounts(data.accounts);
      setHumanAccountId(data.humanAccountId);
      setAccountBalance(data.accountBalance);
      setAccountPositions(data.accountPositions);
    } catch (err) {
      setError(err.message || "Failed to load stock data");
      console.error("Error fetching stock data:", err);
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    stock,
    history,
    accounts,
    humanAccountId,
    accountBalance,
    accountPositions,
    loading,
    error,
    refetch: fetchData,
  };
}

