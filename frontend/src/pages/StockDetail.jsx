import { Link, useParams } from "react-router-dom";
import LoadingWrapper from "../components/common/LoadingWrapper";
import StockChart from "../components/stock/StockChart";
import TradeForm from "../components/trading/TradeForm";
import { useStockDetail } from "../hooks/useStockData";
import { useTrade } from "../hooks/useTrade";
import { calculatePriceChange } from "../utils/stockCalculations";
import { formatCurrency, getPnLClass } from "../utils/formatters";

/**
 * Stock info display component
 */
const StockInfo = ({ stock, priceChange }) => (
  <div className="stock-card">
    <h1 className="stock-details-title">
      {stock.name} ({stock.ticker})
    </h1>

    {stock.description && (
      <p className="stock-details-description">{stock.description}</p>
    )}

    <div className="stock-details-info">
      <div className="stock-info-item">
        <p className="stock-info-label">Current Price</p>
        <p className="stock-info-value">
          {formatCurrency(stock.current_price)}
        </p>
      </div>

      <div className="stock-info-item">
        <p className="stock-info-label">Price Change</p>
        <p className={`stock-info-value ${getPnLClass(priceChange.isPositive)}`}>
          {priceChange.isPositive ? "+" : ""}
          {priceChange.percent}% ({formatCurrency(priceChange.amount, { showSign: true })})
        </p>
      </div>

      <div className="stock-info-item">
        <p className="stock-info-label">Previous Close</p>
        <p className="stock-info-value">
          {formatCurrency(stock.previous_close)}
        </p>
      </div>
    </div>
  </div>
);

/**
 * Stock Detail Page
 * Refactored to use custom hooks and extracted components
 */
const StockDetail = () => {
  const { ticker } = useParams();

  // Use custom hook for stock data
  const {
    stock,
    history,
    accounts,
    humanAccountId,
    accountBalance,
    accountPositions,
    loading,
    error,
    refreshData,
  } = useStockDetail(ticker);

  // Use custom hook for trading
  const trade = useTrade(ticker, humanAccountId, stock);

  // Handle trade submission
  const handleTradeSubmit = async (e) => {
    e.preventDefault();
    await trade.handleTrade(accountBalance, accountPositions, refreshData);
  };

  // Calculate price change
  const priceChange = stock
    ? calculatePriceChange(stock.current_price, stock.previous_close)
    : { percent: "0.00", amount: 0, isPositive: true };

  // Get account name for display
  const accountName = accounts.find((acc) => acc.id === humanAccountId)?.display_name;

  return (
    <LoadingWrapper
      loading={loading}
      error={error}
      showBackLink
      containerClass="stock-details-container"
    >
      {stock && (
        <div className="stock-details-container">
          <Link to="/dashboard">🔙 Back to Dashboard</Link>

          {/* Stock Info */}
          <StockInfo stock={stock} priceChange={priceChange} />

          {/* Price Chart */}
          {history && (
            <div className="stock-card">
              <h2 className="section-title">Price History</h2>
              <StockChart ticker={ticker} historyData={history} />
            </div>
          )}

          {/* Trading Form */}
          <TradeForm
            ticker={ticker}
            currentPrice={stock.current_price}
            accountName={accountName}
            accountBalance={accountBalance}
            accountPositions={accountPositions}
            tradeAction={trade.tradeAction}
            setTradeAction={trade.setTradeAction}
            tradeQuantity={trade.tradeQuantity}
            setTradeQuantity={trade.setTradeQuantity}
            tradeRationale={trade.tradeRationale}
            setTradeRationale={trade.setTradeRationale}
            totalCost={trade.totalCost}
            trading={trade.trading}
            tradeSuccess={trade.tradeSuccess}
            tradeError={trade.tradeError}
            onSubmit={handleTradeSubmit}
            disabled={!humanAccountId}
          />
        </div>
      )}
    </LoadingWrapper>
  );
};

export default StockDetail;
