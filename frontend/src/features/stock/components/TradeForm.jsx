import { formatCurrency, formatShares } from "@/lib/utils";

/**
 * Trade form component
 * Handles buy/sell stock operations
 */
const TradeForm = ({
  // Stock info
  ticker,
  currentPrice,
  
  // Account info
  accountName,
  accountBalance,
  accountPositions,
  
  // Trade state (from useTrade hook)
  tradeAction,
  setTradeAction,
  tradeQuantity,
  setTradeQuantity,
  tradeRationale,
  setTradeRationale,
  totalCost,
  
  // Operation state
  trading,
  tradeSuccess,
  tradeError,
  
  // Handlers
  onSubmit,
  disabled = false,
}) => {
  const upperTicker = ticker?.toUpperCase() || "";
  const currentPosition = accountPositions && upperTicker ? accountPositions[upperTicker] : null;
  const showHoldings = tradeAction === "SELL" && currentPosition;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSubmit) {
      onSubmit(e);
    }
  };

  return (
    <div className="stock-card">
      <h2 className="section-title">Trade Stock</h2>

      {tradeSuccess && <div className="success">{tradeSuccess}</div>}
      {tradeError && <div className="error">{tradeError}</div>}

      <form onSubmit={handleSubmit} className="trading-form">
        {/* Account Info */}
        <div className="form-group">
          <label>Account:</label>
          <input
            type="text"
            value={accountName || "Human Account"}
            disabled
            readOnly
          />
        </div>

        <div className="form-group">
          <label>Balance:</label>
          <input
            type="text"
            value={formatCurrency(accountBalance)}
            disabled
            readOnly
          />
        </div>

        {/* Current Holdings (only shown when selling) */}
        {showHoldings && (
          <div className="form-group">
            <label>Current Holdings:</label>
            <input
              type="text"
              value={formatShares(currentPosition?.quantity || 0)}
              disabled
              readOnly
            />
          </div>
        )}

        {/* Action Select */}
        <div className="form-group">
          <label htmlFor="action">Action:</label>
          <select
            id="action"
            value={tradeAction}
            onChange={(e) => setTradeAction(e.target.value)}
            required
            disabled={trading}
          >
            <option value="BUY">Buy</option>
            <option value="SELL">Sell</option>
          </select>
        </div>

        {/* Quantity */}
        <div className="form-group">
          <label htmlFor="quantity">Quantity:</label>
          <input
            type="number"
            id="quantity"
            min="1"
            step="1"
            value={tradeQuantity}
            onChange={(e) => {
              const value = e.target.value;
              // Allow user to type (including empty string)
              // Validation happens on blur and submit
              setTradeQuantity(value);
            }}
            onBlur={(e) => {
              // Ensure minimum value of 1 on blur
              const value = e.target.value.trim();
              if (value === "") {
                setTradeQuantity(1);
                return;
              }
              const numValue = parseInt(value, 10);
              if (isNaN(numValue) || numValue < 1) {
                setTradeQuantity(1);
              } else {
                setTradeQuantity(numValue);
              }
            }}
            required
            disabled={trading}
          />
        </div>

        {/* Price per Share */}
        <div className="form-group">
          <label htmlFor="price">Price per Share:</label>
          <input
            type="text"
            id="price"
            value={currentPrice ? formatCurrency(currentPrice) : "N/A"}
            disabled
            readOnly
          />
        </div>

        {/* Total Amount */}
        <div className="form-group">
          <label htmlFor="total">Total Amount:</label>
          <input
            type="text"
            id="total"
            value={formatCurrency(totalCost, { fallback: "$0.00" })}
            disabled
            readOnly
          />
        </div>

        {/* Rationale */}
        <div className="form-group">
          <label htmlFor="rationale">Rationale (Optional):</label>
          <textarea
            id="rationale"
            value={tradeRationale}
            onChange={(e) => setTradeRationale(e.target.value)}
            rows="3"
            placeholder="Enter your trading rationale..."
            disabled={trading}
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="btn-primary"
          disabled={trading || disabled || !currentPrice}
          style={{ width: "100%", marginTop: "1rem" }}
        >
          {trading
            ? "Executing..."
            : `${tradeAction} ${typeof tradeQuantity === "number" ? tradeQuantity : parseInt(tradeQuantity, 10) || 1} Share${(typeof tradeQuantity === "number" ? tradeQuantity : parseInt(tradeQuantity, 10) || 1) > 1 ? "s" : ""}`}
        </button>
      </form>
    </div>
  );
};

export default TradeForm;

