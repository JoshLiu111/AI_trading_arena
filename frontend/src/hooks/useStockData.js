import { useState, useEffect, useCallback } from "react";
import { 
  getStockPrices, 
  getStockHistory, 
  getAllAccounts, 
  getAccountPositions 
} from "../services/api";

/**
 * Convert positions array/object to a map for easy lookup
 * Reusable utility for positions data
 */
export const normalizePositions = (positionsData) => {
  const positionsMap = {};
  
  if (!positionsData?.positions) return positionsMap;
  
  const positions = positionsData.positions;
  
  if (Array.isArray(positions)) {
    positions.forEach((pos) => {
      positionsMap[pos.ticker] = pos;
    });
  } else if (typeof positions === "object") {
    Object.keys(positions).forEach((ticker) => {
      positionsMap[ticker] = positions[ticker];
    });
  }
  
  return positionsMap;
};

/**
 * Enhance stock data with fallback prices from history
 */
const enhanceStockWithHistory = (stock, historyData) => {
  const enhanced = { ...stock };
  
  // Fallback for current_price
  if (!enhanced.current_price && historyData?.data?.length > 0) {
    enhanced.current_price = historyData.data[historyData.data.length - 1]?.close || null;
  }
  
  // Set previous_close from history
  if (historyData?.data?.length >= 2) {
    enhanced.previous_close = historyData.data[historyData.data.length - 2]?.close || null;
  } else if (historyData?.data?.length === 1) {
    enhanced.previous_close = historyData.data[0]?.close || null;
  }
  
  return enhanced;
};

/**
 * Hook for fetching single stock detail with related data
 */
export const useStockDetail = (ticker) => {
  const [stock, setStock] = useState(null);
  const [history, setHistory] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [humanAccountId, setHumanAccountId] = useState(null);
  const [accountBalance, setAccountBalance] = useState(0);
  const [accountPositions, setAccountPositions] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!ticker) return;
    
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [stocks, historyData, accountsData] = await Promise.all([
        getStockPrices(),
        getStockHistory(ticker, { days: 7 }),
        getAllAccounts(),
      ]);

      const currentStock = stocks.find((s) => s.ticker === ticker);

      if (!currentStock) {
        throw new Error(`Stock ${ticker} not found`);
      }

      // Enhance stock with history data
      const enhancedStock = enhanceStockWithHistory(currentStock, historyData);

      // Get human account and positions
      const humanAccount = accountsData.find((acc) => acc.account_type === "human");
      
      if (humanAccount) {
        setHumanAccountId(humanAccount.id);
        setAccountBalance(humanAccount.balance || 0);

        try {
          const positionsData = await getAccountPositions(humanAccount.id);
          setAccountBalance(positionsData.balance || humanAccount.balance || 0);
          setAccountPositions(normalizePositions(positionsData));
        } catch (err) {
          console.warn("Failed to fetch account positions:", err);
        }
      }

      setStock(enhancedStock);
      setHistory(historyData);
      setAccounts(accountsData);
    } catch (err) {
      setError(err.message || "Failed to load stock data");
      console.error("Error fetching stock data:", err);
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  // Refresh function for after trades
  const refreshData = useCallback(async () => {
    try {
      const [stocks, historyData] = await Promise.all([
        getStockPrices(),
        getStockHistory(ticker, { days: 7 }),
      ]);

      const currentStock = stocks.find((s) => s.ticker === ticker);
      if (currentStock) {
        setStock(enhanceStockWithHistory(currentStock, historyData));
      }

      // Refresh accounts
      const accountsData = await getAllAccounts();
      setAccounts(accountsData);

      // Refresh positions
      if (humanAccountId) {
        try {
          const positionsData = await getAccountPositions(humanAccountId);
          setAccountBalance(positionsData.balance || 0);
          setAccountPositions(normalizePositions(positionsData));
        } catch (err) {
          console.warn("Failed to refresh account positions:", err);
        }
      }
    } catch (err) {
      console.error("Error refreshing data:", err);
    }
  }, [ticker, humanAccountId]);

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
    refreshData,
  };
};

/**
 * Hook for fetching stocks list (for Dashboard)
 */
export const useStocksList = () => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStocks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getStockPrices();
      setStocks(data);
    } catch (err) {
      setError(err.message || "Failed to load stocks");
      console.error("Error fetching stocks:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStocks();
  }, [fetchStocks]);

  return { stocks, loading, error, refetch: fetchStocks };
};

export default useStockDetail;
