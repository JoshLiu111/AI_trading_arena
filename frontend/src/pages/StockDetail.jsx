import { Link, useParams } from "react-router-dom";
import { LoadingWrapper } from "@/ui";
import { StockChart, TradeForm } from "@/features/stock";
import { useStockDetail } from "@/features/stock/hooks/useStockDetail";
import { useTrade } from "@/features/stock/hooks/useTrade";
import { calculatePriceChange, formatCurrency, getPnLClass } from "@/lib/utils";

/**
 * Stock info display component
 */
const StockInfo = ({ stock, priceChange }) => (
  <div className="stock-card">
    <h1 className="stock-details-title">
      {stock.name}
    </h1>

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

    {/* Company Information */}
    {(stock.description || stock.sector || stock.industry || stock.homepage_url || stock.website) ? (
      <div className="stock-company-info">
        <h3 className="stock-company-info-title">Company Information</h3>
        <div className="stock-company-info-content">
          {stock.description && stock.description.trim() !== "" && (
            <div className="stock-company-info-description">
              <p className="stock-company-info-description-text">{stock.description}</p>
            </div>
          )}
          {(stock.sector && stock.sector.trim() !== "") && (
            <div className="stock-company-info-item">
              <span className="stock-company-info-label">Sector:</span>
              <span className="stock-company-info-value">{stock.sector}</span>
            </div>
          )}
          {(stock.industry && stock.industry.trim() !== "") && (
            <div className="stock-company-info-item">
              <span className="stock-company-info-label">Industry:</span>
              <span className="stock-company-info-value">{stock.industry}</span>
            </div>
          )}
          {((stock.homepage_url && stock.homepage_url.trim() !== "") || (stock.website && stock.website.trim() !== "")) && (
            <div className="stock-company-info-item">
              <span className="stock-company-info-label">Website:</span>
              <a 
                href={stock.homepage_url || stock.website} 
                target="_blank" 
                rel="noopener noreferrer"
                className="stock-company-info-link"
              >
                {stock.homepage_url || stock.website}
              </a>
            </div>
          )}
        </div>
      </div>
    ) : (
      // Debug: Show message if no company info available
      <div className="stock-company-info">
        <p style={{ color: '#999', fontSize: '0.9rem', fontStyle: 'italic' }}>
          Company information not available yet. It will be loaded in the background.
        </p>
      </div>
    )}
  </div>
);

/**
 * Stock Detail Page
 * Uses hooks for data fetching and trade operations
 */
const StockDetail = () => {
  const { ticker } = useParams();
  const {
    stock,
    history,
    accounts,
    humanAccountId,
    accountBalance,
    accountPositions,
    loading,
    error,
    refetch,
  } = useStockDetail(ticker);

  const {
    tradeAction,
    setTradeAction,
    tradeQuantity,
    setTradeQuantity,
    tradeRationale,
    setTradeRationale,
    totalCost,
    trading,
    tradeSuccess,
    tradeError,
    handleTradeSubmit,
  } = useTrade({
    ticker,
    stock,
    accountId: humanAccountId,
    accountBalance,
    accountPositions,
    onSuccess: refetch,
  });

  // Calculate price change
  const priceChange = stock
    ? calculatePriceChange(stock.current_price, stock.previous_close)
    : { percent: "0.00", amount: 0, isPositive: true };


  // Get account name for display (with null safety)
  const accountName = accounts && Array.isArray(accounts) && humanAccountId
    ? accounts.find((acc) => acc?.id === humanAccountId)?.display_name
    : null;

  return (
    <LoadingWrapper
      loading={loading}
      error={error}
      showBackLink
      containerClass="stock-details-container"
    >
      {stock && (
        <>
          <Link to="/dashboard">🔙 Back to Dashboard</Link>

          {/* Main content: Left (Stock Info + Chart) and Right (Trading Form) */}
          <div className="stock-details-layout">
            {/* Left side: Stock Info and Chart */}
            <div className="stock-details-left">
              {/* Stock Info */}
              <StockInfo stock={stock} priceChange={priceChange} />

              {/* Price Chart */}
              {history && (
                <div className="stock-card">
                  <h2 className="section-title">Price History</h2>
                  <StockChart ticker={ticker} historyData={history} />
                </div>
              )}
            </div>

            {/* Right side: Trading Form */}
            <div className="stock-details-right">
              <TradeForm
                ticker={ticker}
                currentPrice={stock.current_price}
                accountName={accountName}
                accountBalance={accountBalance}
                accountPositions={accountPositions}
                tradeAction={tradeAction}
                setTradeAction={setTradeAction}
                tradeQuantity={tradeQuantity}
                setTradeQuantity={setTradeQuantity}
                tradeRationale={tradeRationale}
                setTradeRationale={setTradeRationale}
                totalCost={totalCost}
                trading={trading}
                tradeSuccess={tradeSuccess}
                tradeError={tradeError}
                onSubmit={handleTradeSubmit}
                disabled={!humanAccountId}
              />
            </div>
          </div>
        </>
      )}
    </LoadingWrapper>
  );
};

export default StockDetail;
