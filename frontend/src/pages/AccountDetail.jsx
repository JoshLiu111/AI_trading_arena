import { Link, useParams } from "react-router-dom";
import { LoadingWrapper } from "@/ui";
import { PositionsTable, TransactionsTable } from "@/features/account";
import { useAccount } from "@/features/account/hooks/useAccount";
import { formatCurrency, formatPnL, formatDate, getPnLClass } from "@/lib/utils";

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
 * Uses hooks for data fetching, pages only handle composition
 */
const AccountDetail = () => {
  const { accountId } = useParams();
  const { account, positions, transactions, loading, error } = useAccount(accountId);

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
