import CompetitionStepWrapper from "./CompetitionStepWrapper";

/**
 * Strategy Generation Step Component
 * Handles strategy generation and display
 * 
 * @param {Object} props
 * @param {string|null} props.strategy - The strategy text to display
 * @param {boolean} props.loading - Whether the competition is starting
 * @param {boolean} props.generatingStrategy - Whether a strategy is being generated
 * @param {Function} props.onGenerate - Callback to generate a new strategy
 * @param {Function} props.onRegenerate - Callback to regenerate the strategy
 * @param {Function} props.onStartTrading - Callback to start trading
 */
const StrategyGenerationStep = ({
  strategy,
  loading,
  generatingStrategy,
  onGenerate,
  onRegenerate,
  onStartTrading,
}) => {
  return (
    <CompetitionStepWrapper
      actions={
        !strategy ? (
          <button
            onClick={onGenerate}
            disabled={generatingStrategy}
            className="btn-primary competition-btn"
          >
            {generatingStrategy ? "Generating..." : "Generate Strategy Report"}
          </button>
        ) : (
          <>
            <button
              onClick={onRegenerate}
              disabled={generatingStrategy}
              className="btn-secondary competition-btn"
            >
              {generatingStrategy ? "Regenerating..." : "Regenerate Strategy Report"}
            </button>
            <button
              onClick={onStartTrading}
              disabled={generatingStrategy || loading}
              className="btn-primary competition-btn"
            >
              {loading ? "Starting Competition (this may take a few minutes)..." : "Start Trading"}
            </button>
          </>
        )
      }
    >
      <div className="strategy-container">
        {loading && (
          <div className="strategy-loading">
            <p>Starting competition... This may take a few minutes.</p>
            <p>Please wait while we:</p>
            <ul style={{ textAlign: "left", margin: "10px 0" }}>
              <li>Reset accounts</li>
              <li>Refresh stock data</li>
              <li>Generate AI trading strategies</li>
            </ul>
          </div>
        )}
        {!strategy && !generatingStrategy && !loading && (
          <div className="strategy-placeholder">
            <p>Click the button below to view the AI-generated trading strategy</p>
          </div>
        )}
        {generatingStrategy && !loading ? (
          <div className="strategy-loading">
            <p>Loading trading strategy...</p>
          </div>
        ) : strategy && !loading ? (
          <div className="strategy-display">
            <textarea
              className="strategy-textarea"
              value={strategy}
              readOnly
              rows={Math.max(20, strategy.split('\n').length + 2)}
            />
          </div>
        ) : null}
      </div>
    </CompetitionStepWrapper>
  );
};

export default StrategyGenerationStep;
