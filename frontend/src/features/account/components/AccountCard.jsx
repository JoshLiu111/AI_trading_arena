import { Link } from "react-router-dom";
import { formatCurrency, formatPnL, getPnLClass } from "@/lib/utils";

/**
 * Account card component
 * Displays account summary with P&L
 */
const AccountCard = ({ account }) => {
  const pnl = formatPnL(account.total_value, account.initial_balance);

  return (
    <Link to={`/account/${account.id}`} className="account-card-link">
      <div className="account-card">
        <h3 className="account-name">{account.display_name}</h3>
        <p className="account-type">{account.account_type} Account</p>
        
        <div className="account-info">
          <div className="account-info-row">
            <span className="account-label">Balance:</span>
            <span className="account-value">
              {formatCurrency(account.balance)}
            </span>
          </div>
          
          <div className="account-info-row">
            <span className="account-label">Total Value:</span>
            <span className="account-value">
              {formatCurrency(account.total_value)}
            </span>
          </div>
          
          <div className="account-info-row">
            <span className="account-label">P&L:</span>
            <span className={`account-value ${getPnLClass(pnl.isPositive)}`}>
              {formatCurrency(pnl.amount, { showSign: true })}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default AccountCard;

