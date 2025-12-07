import { Link } from "react-router-dom";
import { calculatePriceChange } from "../../utils/stockCalculations";
import { formatCurrency, getPnLClass } from "../../utils/formatters";

const StockCard = ({ stock }) => {
  const { percent: priceChangePercent, isPositive } = calculatePriceChange(
    stock.current_price,
    stock.previous_close
  );

  // Handle null/undefined/0 price
  const displayPrice = stock.current_price && stock.current_price > 0 
    ? formatCurrency(stock.current_price)
    : "N/A";

  return (
    <Link to={`/stock/${stock.ticker}`}>
      <div className="stock-card">
        <h2 className="stock-ticker">{stock.ticker.toUpperCase()}</h2>
        <p className="stock-name">{stock.name || stock.ticker}</p>
        <div className="stock-price-row">
          <span className="stock-price">{displayPrice}</span>
          {stock.current_price && stock.current_price > 0 && (
            <span className={`stock-change ${getPnLClass(isPositive)}`}>
              {isPositive ? "+" : ""}
              {priceChangePercent}%
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default StockCard;
