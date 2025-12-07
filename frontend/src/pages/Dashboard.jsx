import { useState, useEffect, useMemo, useRef } from "react";
import { 
  Spinner, 
  FilterInput, 
  SortSelector, 
  CompetitionFlow, 
  AccountCard 
} from "../components";
import StockCard from "../components/stock/StockCard";
import { getStockPrices, getAllAccounts, getCompetitionStatus, getLatestStrategy } from "../services/api";
import { formatStrategyContent } from "../utils/formatStrategy";
import { ACCOUNT_TYPES, SORT_OPTIONS, API_DEFAULTS } from "../constants";

function Dashboard() {
  const [stocks, setStocks] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [competitionStatus, setCompetitionStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("");
  const [sortBy, setSortBy] = useState(SORT_OPTIONS.PRICE_DESC);
  const [aiStrategyReport, setAiStrategyReport] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [stocksData, accountsData, statusData] = await Promise.all([
        getStockPrices(),        // GET /api/v1/stocks/prices
    getAllAccounts(),        // GET /api/v1/accounts
    getCompetitionStatus(),  // GET /api/v1/competition/status
      ]);
      setStocks(stocksData);
      setAccounts(accountsData);
      setCompetitionStatus(statusData);
    } catch (err) {
      setError(err.message);
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Fetch AI strategy report when competition is running
  const lastIsRunningRef = useRef(null);
  useEffect(() => {
    const fetchAiStrategyReport = async () => {
      // Only fetch if is_running actually changed
      if (lastIsRunningRef.current === competitionStatus?.is_running) {
        return; // No change, skip
      }
      
      lastIsRunningRef.current = competitionStatus?.is_running;
      
      if (!competitionStatus?.is_running) {
        setAiStrategyReport(null);
        return;
      }

      const aiAccount = accounts?.find(acc => acc.account_type === ACCOUNT_TYPES.AI);
      const aiAccountId = aiAccount?.id || API_DEFAULTS.DEFAULT_AI_ACCOUNT_ID;
      
      if (aiAccountId) {
        try {
          const strategyData = await getLatestStrategy(aiAccountId);
          const strategyText = formatStrategyContent(strategyData);
          setAiStrategyReport(strategyText);
        } catch (err) {
          console.error("Error fetching AI strategy report:", err);
        }
      }
    };

    fetchAiStrategyReport();
  }, [competitionStatus?.is_running]); // Removed accounts dependency to prevent loops

  const handleCompetitionStatusChange = async (newStatus) => {
    // Only update if status actually changed to prevent unnecessary re-renders
    if (competitionStatus?.is_running === newStatus?.is_running && 
        competitionStatus?.is_paused === newStatus?.is_paused) {
      return; // No actual change, skip update
    }
    
    setCompetitionStatus(newStatus);
    // Refresh accounts when competition status changes (especially after start)
    if (newStatus?.is_running) {
      try {
        const accountsData = await getAllAccounts();
        setAccounts(accountsData);
      } catch (err) {
        console.error("Error refreshing accounts:", err);
      }
    }
  };

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
      <div className="spinner-container">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        ❌ Error: {error}
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-content">
        <div className="dashboard-header">
          <h1>Stock Trading Arena</h1>
          <p className="dashboard-subtitle">
            AI vs Human Stock Trading Competition
          </p>
        </div>

        <section className="dashboard-section">
          <CompetitionFlow 
            competitionStatus={competitionStatus} 
            onStatusChange={handleCompetitionStatusChange}
            accounts={accounts}
          />
        </section>

        {/* AI Strategy Report Display */}
        {competitionStatus?.is_running && aiStrategyReport && (
          <section className="dashboard-section">
            <div className="ai-strategy-report">
              <h2 className="section-title">AI Strategy Report</h2>
              <div className="strategy-report-content">
                <p className="strategy-report-text">{aiStrategyReport}</p>
              </div>
            </div>
          </section>
        )}

        <section className="dashboard-section">
          <h2 className="section-title">Accounts</h2>
          <div className="account-grid">
            {accounts.map((account) => (
              <AccountCard key={account.id} account={account} />
            ))}
          </div>
        </section>

        <section className="dashboard-section">
          <h2 className="section-title">Stocks</h2>
          <div className="top-controls">
            <FilterInput filter={filter} onFilterChange={setFilter} />
            <SortSelector sortBy={sortBy} onSortChange={setSortBy} />
          </div>
          <div className="stock-grid">
            {filteredAndSortedStocks.length === 0 ? (
              <p className="no-data-message">No stocks available. Please start the competition to load stock data.</p>
            ) : (
              filteredAndSortedStocks.map((stock) => (
                <StockCard key={stock.ticker} stock={stock} />
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
