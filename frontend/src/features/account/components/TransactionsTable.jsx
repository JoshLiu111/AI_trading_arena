import { Link } from "react-router-dom";
import { formatCurrency, formatDate } from "@/lib/utils";

/**
 * Transactions table component
 * Displays account transaction history
 */
const TransactionsTable = ({ transactions = [] }) => {
  if (transactions.length === 0) {
    return <p className="no-data-message">No transactions found.</p>;
  }

  return (
    <div className="transactions-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Ticker</th>
            <th>Action</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Total Amount</th>
            <th>Rationale</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.id}>
              <td>{formatDate(transaction.executed_at, { includeTime: true })}</td>
              <td>
                <Link to={`/stock/${transaction.ticker}`} className="ticker-link">
                  {transaction.ticker}
                </Link>
              </td>
              <td>
                <span
                  className={`action-badge ${
                    transaction.action === "BUY" ? "buy" : "sell"
                  }`}
                >
                  {transaction.action}
                </span>
              </td>
              <td>{transaction.quantity}</td>
              <td>{formatCurrency(transaction.price)}</td>
              <td>{formatCurrency(transaction.total_amount)}</td>
              <td className="rationale-cell">
                {transaction.rationale || "N/A"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TransactionsTable;
