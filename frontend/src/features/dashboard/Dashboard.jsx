import { useState, useEffect, useCallback } from "react";
import { Spinner } from "@/ui";
import { CompetitionFlow } from "@/features/competition";
import { AccountCard } from "@/features/account";
import { StockList } from "@/features/stock";
import { StrategyReport } from "@/features/strategyReport";
import { getAllAccounts } from "@/lib/api";

function Dashboard() {
  const [accounts, setAccounts] = useState([]);
  const [competitionStatus, setCompetitionStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch accounts on mount
  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        setLoading(true);
        setError(null);
        const accountsData = await getAllAccounts();
        setAccounts(accountsData);
      } catch (err) {
        setError(err.message);
        console.error("Error fetching accounts:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAccounts();
  }, []);

  // Auto-refresh accounts every 15 seconds when competition is running
  useEffect(() => {
    if (!competitionStatus?.is_running) {
      return; // Don't refresh if competition is not running
    }

    const refreshInterval = setInterval(async () => {
      try {
        const accountsData = await getAllAccounts();
        setAccounts(accountsData);
      } catch (err) {
        console.error("Error auto-refreshing accounts:", err);
      }
    }, 15000); // 15 seconds

    return () => clearInterval(refreshInterval);
  }, [competitionStatus?.is_running]);

  // Handle competition status change from CompetitionFlow
  // Use useCallback to prevent unnecessary re-renders
  const handleCompetitionStatusChange = useCallback(async (newStatus) => {
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
  }, []);

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

        {/* AI Strategy Report */}
        <StrategyReport 
          competitionStatus={competitionStatus}
          accounts={accounts}
        />

        <section className="dashboard-section">
          <h2 className="section-title">Accounts</h2>
          <div className="account-grid">
            {accounts.map((account) => (
              <AccountCard key={account.id} account={account} />
            ))}
          </div>
        </section>

        {/* Stock List */}
        <StockList 
          competitionStatus={competitionStatus}
        />
      </div>
    </div>
  );
}

export default Dashboard;
