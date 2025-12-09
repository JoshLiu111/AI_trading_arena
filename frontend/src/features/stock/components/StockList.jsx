import { useState, useEffect, useMemo, useRef } from "react";
import { FilterInput, SortSelector } from "@/ui";
import StockCard from "./StockCard";
import { getStockPrices } from "@/lib/api";
import { SORT_OPTIONS } from "@/lib/constants";

/**
 * Stock List Component
 * Fetches and displays stock list with filtering and sorting
 * 
 * @param {Object} props
 * @param {Object|null} props.competitionStatus - Competition status object
 * @param {Function} props.onStocksUpdate - Optional callback when stocks are updated
 */
const StockList = ({ competitionStatus, onStocksUpdate }) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("");
  const [sortBy, setSortBy] = useState(SORT_OPTIONS.PRICE_DESC);
  
  // Use ref to store callback to avoid dependency issues
  const onStocksUpdateRef = useRef(onStocksUpdate);
  useEffect(() => {
    onStocksUpdateRef.current = onStocksUpdate;
  }, [onStocksUpdate]);

  // Initial fetch
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        setLoading(true);
        setError(null);
        const stocksData = await getStockPrices();
        setStocks(stocksData);
        if (onStocksUpdateRef.current) {
          onStocksUpdateRef.current(stocksData);
        }
      } catch (err) {
        setError(err.message);
        console.error("Error fetching stocks:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStocks();
  }, []);

  // Auto-refresh stock prices every 5 minutes when competition is running
  useEffect(() => {
    if (!competitionStatus?.is_running) {
      return; // Don't refresh if competition is not running
    }

    const refreshInterval = setInterval(async () => {
      try {
        const stocksData = await getStockPrices();
        setStocks(stocksData);
        if (onStocksUpdateRef.current) {
          onStocksUpdateRef.current(stocksData);
        }
      } catch (err) {
        console.error("Error auto-refreshing stocks:", err);
      }
    }, 300000); // 5 minutes (300000 ms)

    // Cleanup interval on unmount or when competition stops
    return () => clearInterval(refreshInterval);
  }, [competitionStatus?.is_running]);

  // Filter and sort stocks
  const filteredAndSortedStocks = useMemo(() => {
    let filtered = stocks;

    // Apply filter
    if (filter) {
      const filterLower = filter.toLowerCase();
      filtered = stocks.filter(
        (stock) =>
          stock.name.toLowerCase().includes(filterLower) ||
          stock.ticker.toLowerCase().includes(filterLower)
      );
    }

    // Apply sort
    const sorted = [...filtered].sort((a, b) => {
      // Calculate price change percentage, handle division by zero
      const priceChangeA = a.previous_close && a.previous_close !== 0
        ? ((a.current_price - a.previous_close) / a.previous_close) * 100
        : 0;
      const priceChangeB = b.previous_close && b.previous_close !== 0
        ? ((b.current_price - b.previous_close) / b.previous_close) * 100
        : 0;

      switch (sortBy) {
        case SORT_OPTIONS.PRICE_DESC:
          return b.current_price - a.current_price;
        case SORT_OPTIONS.PRICE_ASC:
          return a.current_price - b.current_price;
        case SORT_OPTIONS.CHANGE_DESC:
          return priceChangeB - priceChangeA;
        case SORT_OPTIONS.CHANGE_ASC:
          return priceChangeA - priceChangeB;
        default:
          return 0;
      }
    });

    return sorted;
  }, [stocks, filter, sortBy]);

  if (loading) {
    return (
      <section className="dashboard-section">
        <h2 className="section-title">Stocks</h2>
        <div className="spinner-container">
          <p>Loading stocks...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="dashboard-section">
        <h2 className="section-title">Stocks</h2>
        <div className="error">
          ❌ Error: {error}
        </div>
      </section>
    );
  }

  return (
    <section className="dashboard-section">
      <h2 className="section-title">Stocks</h2>
      <div className="top-controls">
        <FilterInput filter={filter} onFilterChange={setFilter} />
        <SortSelector sortBy={sortBy} onSortChange={setSortBy} />
      </div>
      <div className="stock-grid">
        {filteredAndSortedStocks.length === 0 ? (
          <p className="no-data-message">
            No stocks available. Please start the competition to load stock data.
          </p>
        ) : (
          filteredAndSortedStocks.map((stock) => (
            <StockCard key={stock.ticker} stock={stock} />
          ))
        )}
      </div>
    </section>
  );
};

export default StockList;

