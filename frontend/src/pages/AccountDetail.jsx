import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import LoadingWrapper from "../components/common/LoadingWrapper";
import PositionsTable from "../components/account/PositionsTable";
import TransactionsTable from "../components/account/TransactionsTable";
import { formatCurrency, formatPnL, formatDate, getPnLClass } from "../utils/formatters";
import {
  getAccountById,
  getAccountTransactions,
  getAccountPositions,
} from "../services/api";

/**
 * Account overview grid item
 */
const OverviewItem = ({ label, value, className = "" }) => (
  <div className="account-overview-item">
    <p className="stock-info-label">{label}</p>
    <p className={`stock-info-value ${className}`}>{value}</p>
  </div>
);

/**
 * Account Detail Page
 * Displays account info, positions, and transaction history
 */
const AccountDetail = () => {
  const { accountId } = useParams();
  const [account, setAccount] = useState(null);
  const [positions, setPositions] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAccountData = async () => {
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
        // positions format: { "AAPL": { quantity, avg_price, total_cost }, ... }
        let positionsArray = [];
        if (positionsData?.positions && typeof positionsData.positions === 'object') {
          positionsArray = Object.entries(positionsData.positions).map(([ticker, data]) => ({
            ticker,
            quantity: data.quantity || 0,
            average_price: data.avg_price || 0,
            total_value: (data.avg_price || 0) * (data.quantity || 0),
            current_price: data.avg_price || 0, // Will be updated with real-time price if needed
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

    if (accountId) {
      fetchAccountData();
    }
  }, [accountId]);

  // Calculate P&L
  const pnl = account ? formatPnL(account.total_value, account.initial_balance) : null;

  return (
    <LoadingWrapper
      loading={loading}
      error={error}
      showBackLink
      containerClass="account-details-container"
    >
      {account && (
        <div className="account-details-container">
          <Link to="/dashboard" className="back-link">
            🔙 Back to Dashboard
          </Link>

          {/* Account Overview */}
          <div className="stock-card account-overview-card">
            <h1 className="stock-details-title">
              {account.display_name} ({account.account_type.toUpperCase()} Account)
            </h1>

            <div className="account-overview-grid">
              <OverviewItem label="Account ID" value={`#${account.id}`} />
              <OverviewItem label="Account Name" value={account.account_name} />
              <OverviewItem 
                label="Initial Balance" 
                value={formatCurrency(account.initial_balance)} 
              />
              <OverviewItem 
                label="Current Balance" 
                value={formatCurrency(account.balance)} 
              />
              <OverviewItem 
                label="Total Value" 
                value={formatCurrency(account.total_value)} 
              />
              <OverviewItem
                label="Profit & Loss"
                value={pnl.formatted}
                className={getPnLClass(pnl.isPositive)}
              />
              {account.created_at && (
                <OverviewItem
                  label="Created At"
                  value={formatDate(account.created_at)}
                />
              )}
            </div>
          </div>

          {/* Positions */}
          <div className="stock-card">
            <h2 className="section-title">Current Positions</h2>
            <PositionsTable positions={positions} />
          </div>

          {/* Transactions */}
          <div className="stock-card">
            <h2 className="section-title">Transaction History</h2>
            <TransactionsTable transactions={transactions} />
          </div>
        </div>
      )}
    </LoadingWrapper>
  );
};

export default AccountDetail;
