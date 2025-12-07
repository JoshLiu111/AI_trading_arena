import { Link } from "react-router-dom";
import { formatCurrency, formatPnL, getPnLClass } from "../../utils/formatters";

/**
 * Positions table component
 * Displays account positions with P&L
 */
const PositionsTable = ({ positions = [] }) => {
  if (positions.length === 0) {
    return <p className="no-data-message">No positions found.</p>;
  }

  return (
    <div className="positions-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Quantity</th>
            <th>Avg Price</th>
            <th>Current Price</th>
            <th>Total Value</th>
            <th>P&L</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((position, index) => {
            const pnl = formatPnL(
              position.current_price * position.quantity,
              position.average_price * position.quantity
            );

            return (
              <tr key={position.ticker || index}>
                <td>
                  <Link to={`/stock/${position.ticker}`} className="ticker-link">
                    {position.ticker}
                  </Link>
                </td>
                <td>{position.quantity}</td>
                <td>{formatCurrency(position.average_price)}</td>
                <td>{formatCurrency(position.current_price)}</td>
                <td>{formatCurrency(position.total_value)}</td>
                <td className={getPnLClass(pnl.isPositive)}>
                  {pnl.formatted}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default PositionsTable;
