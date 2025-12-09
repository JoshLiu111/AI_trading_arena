import { Link } from "react-router-dom";
import { calculatePriceChange, formatCurrency, getPnLClass } from "@/lib/utils";

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
        {/* First line: ticker */}
        <h2 className="stock-ticker">{stock.ticker.toUpperCase()}</h2>
        {/* Second line: price change */}
        {stock.current_price && stock.current_price > 0 ? (
          <p className={`stock-change ${getPnLClass(isPositive)}`}>
            {isPositive ? "+" : ""}
            {priceChangePercent}%
          </p>
        ) : (
          <p className="stock-change">N/A</p>
        )}
        {/* Third line: current price */}
        <p className="stock-price">{displayPrice}</p>
      </div>
    </Link>
  );
};

export default StockCard;

