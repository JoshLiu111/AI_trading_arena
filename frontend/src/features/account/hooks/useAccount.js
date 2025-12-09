import { useState, useEffect } from "react";
import {
  getAccountById,
  getAccountTransactions,
  getAccountPositions,
} from "@/lib/api";

/**
 * Custom hook for fetching account data
 * @param {number|string} accountId - The account ID
 * @returns {object} Account data, positions, transactions, loading, and error states
 */
export function useAccount(accountId) {
  const [account, setAccount] = useState(null);
  const [positions, setPositions] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAccountData = async () => {
      if (!accountId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const [accountData, positionsData, transactionsData] = await Promise.all([
          getAccountById(parseInt(accountId)),
          getAccountPositions(parseInt(accountId)),
          getAccountTransactions(parseInt(accountId)),
        ]);

        if (!accountData) {
          throw new Error(`Account ${accountId} not found`);
        }

        setAccount(accountData);
        
        // Handle positions: backend returns { positions: {...} }, convert to array
        // positions format: { "AAPL": { quantity, avg_price, total_cost, current_price }, ... }
        // current_price is from backend's real-time price service
        let positionsArray = [];
        if (positionsData?.positions && typeof positionsData.positions === 'object') {
          positionsArray = Object.entries(positionsData.positions).map(([ticker, data]) => ({
            ticker,
            quantity: data.quantity || 0,
            average_price: data.avg_price || 0, // Cost per share
            current_price: data.current_price || null, // Real-time price from backend
            total_value: (data.current_price || 0) * (data.quantity || 0), // Current market value
          }));
        } else if (Array.isArray(positionsData)) {
          positionsArray = positionsData;
        }
        setPositions(positionsArray);
        setTransactions(transactionsData || []);
      } catch (err) {
        setError(err.message || "Failed to load account data");
        console.error("Error fetching account data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAccountData();
  }, [accountId]);

  return {
    account,
    positions,
    transactions,
    loading,
    error,
  };
}
