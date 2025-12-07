import { useState, useEffect, useRef } from "react";
import { 
  getLatestStrategy, 
  startCompetition,
  generateStrategy,
  regenerateStrategy,
  pauseCompetition, 
  resumeCompetition, 
  getCompetitionStatus 
} from "../../services/api";
import { ACCOUNT_TYPES, API_DEFAULTS } from "../../constants";

// Reusable Step Content Wrapper
const StepContent = ({ children, actions }) => (
  <div className="step-content">
    {children}
    <div className="step-actions-centered">
      {actions}
    </div>
  </div>
);

const CompetitionFlow = ({ competitionStatus, onStatusChange, accounts }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatingStrategy, setGeneratingStrategy] = useState(false);
  
  // Use refs to prevent infinite loops
  const isAutoLoadingRef = useRef(false);
  const lastIsRunningRef = useRef(null);
  const lastStrategyRef = useRef(null);

  // Get AI account ID (assuming first AI account) - memoize to prevent unnecessary recalculations
  const aiAccountId = useRef(null);
  useEffect(() => {
    const aiAccount = accounts?.find(acc => acc.account_type === ACCOUNT_TYPES.AI);
    aiAccountId.current = aiAccount?.id || API_DEFAULTS.DEFAULT_AI_ACCOUNT_ID;
  }, [accounts]);

  const { is_running, is_paused } = competitionStatus || {};

  // Sync currentStep with competition status (only when status actually changes)
  useEffect(() => {
    // Only update if is_running or strategy actually changed
    if (lastIsRunningRef.current === is_running && lastStrategyRef.current === strategy) {
      return; // No change, skip update
    }
    
    // Store previous values before updating
    const prevIsRunning = lastIsRunningRef.current;
    const prevStrategy = lastStrategyRef.current;
    
    // Update refs first
    lastIsRunningRef.current = is_running;
    lastStrategyRef.current = strategy;
    
    // Only update step if there's a meaningful change and we're not currently loading
    if (loading) {
      // Don't change step while loading to prevent loops
      return;
    }
    
    if (is_running && prevIsRunning !== is_running) {
      // Competition just started - go to Step 3
      setCurrentStep(3);
    } else if (!is_running && strategy && !prevStrategy) {
      // Strategy just loaded and competition not running - go to Step 2
      setCurrentStep(2);
    } else if (!is_running && !strategy && prevStrategy) {
      // Strategy was cleared - go to Step 1
      setCurrentStep(1);
    }
    // Don't change step if just strategy content changed but competition is running
  }, [is_running, strategy, loading]);

  // Auto-load strategy when in Step 2 and strategy is not loaded (only once per step change)
  useEffect(() => {
    // Only auto-load if we're in Step 2, no strategy loaded, not currently generating, and not already loading
    if (currentStep === 2 && !strategy && !generatingStrategy && !isAutoLoadingRef.current && aiAccountId.current) {
      isAutoLoadingRef.current = true;
      
      const loadStrategyIfNeeded = async () => {
        try {
          setGeneratingStrategy(true);
          const strategyData = await getLatestStrategy(aiAccountId.current);
          
          let strategyText = "";
          if (strategyData.content) {
            strategyText = JSON.stringify(strategyData.content, null, 2);
          } else if (strategyData.strategy_content) {
            try {
              const parsed = JSON.parse(strategyData.strategy_content);
              strategyText = JSON.stringify(parsed, null, 2);
            } catch {
              strategyText = strategyData.strategy_content;
            }
          } else if (strategyData.strategy === null || !strategyData.strategy) {
            // No strategy available, don't set it
            isAutoLoadingRef.current = false;
            return;
          } else {
            strategyText = JSON.stringify(strategyData, null, 2);
          }
          
          if (strategyText) {
            setStrategy(strategyText);
          }
        } catch (err) {
          // Silently fail - strategy might not exist yet
          console.log("No strategy available yet:", err.message);
        } finally {
          setGeneratingStrategy(false);
          // Reset flag after a delay to allow state to settle
          setTimeout(() => {
            isAutoLoadingRef.current = false;
          }, 100);
        }
      };

      loadStrategyIfNeeded();
    }
  }, [currentStep]); // Only depend on currentStep to prevent loops

  // Step 1: Start/Restart Competition - Just navigate to step 2
  const handleStartCompetition = () => {
    // Reset auto-loading flag when manually navigating
    isAutoLoadingRef.current = false;
    // Clear strategy to ensure fresh load
    setStrategy(null);
    setCurrentStep(2);
    setError(null);
  };

  const handleRestartCompetition = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to restart the competition? This will reset all accounts and clear all trading history."
    );
    
    if (!confirmed) return;

    try {
      setLoading(true);
      setError(null);
      // Reset competition state
      await startCompetition();
      const newStatus = await getCompetitionStatus();
      onStatusChange(newStatus);
      // Clear strategy and go to step 2
      setStrategy(null);
      setCurrentStep(2);
    } catch (err) {
      setError(err.message || "Failed to restart competition");
      console.error("Error restarting competition:", err);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Generate Strategy
  const handleGenerateStrategy = async (isRegenerate = false) => {
    try {
      setGeneratingStrategy(true);
      setError(null);
      
      const accountId = aiAccountId.current || API_DEFAULTS.DEFAULT_AI_ACCOUNT_ID;
      
      if (isRegenerate) {
        // Regenerate: Delete existing strategies and generate new ones
        try {
          await regenerateStrategy(accountId);
          // Wait a bit for strategy to be generated
          await new Promise((resolve) => setTimeout(resolve, 1000));
        } catch (err) {
          console.error("Error regenerating strategy:", err);
          setError("Failed to regenerate strategy. Please try again.");
          return;
        }
      } else {
        // Generate: Only generate strategy (no delete, no reset)
        try {
          await generateStrategy(accountId);
          // Wait a bit for strategy to be generated
          await new Promise((resolve) => setTimeout(resolve, 1000));
        } catch (err) {
          console.error("Error generating strategy:", err);
          setError("Failed to generate strategy. Please try again.");
          return;
        }
      }
      
      // Fetch the generated strategy
      const strategyData = await getLatestStrategy(accountId);
      
      let strategyText = "";
      
      if (strategyData.content) {
        strategyText = JSON.stringify(strategyData.content, null, 2);
      } else if (strategyData.strategy_content) {
        try {
          const parsed = JSON.parse(strategyData.strategy_content);
          strategyText = JSON.stringify(parsed, null, 2);
        } catch {
          strategyText = strategyData.strategy_content;
        }
      } else if (strategyData.strategy === null) {
        strategyText = "No strategy available yet. Please wait for the strategy to be generated.";
      } else {
        strategyText = JSON.stringify(strategyData, null, 2);
      }
      
      setStrategy(strategyText);
    } catch (err) {
      setError(err.message || "Failed to generate strategy");
      console.error("Error generating strategy:", err);
    } finally {
      setGeneratingStrategy(false);
    }
  };

  // Step 2: Start Trading
  const handleStartTrading = async () => {
    if (!strategy) {
      setError("Please generate a strategy report first");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Start competition (this will reset accounts, refresh data, and set is_running=true)
      // Note: This may take a while (refresh stock data, generate AI strategy)
      console.log("Starting competition... This may take a few minutes.");
      const result = await startCompetition();
      console.log("Competition started:", result);
      
      // Get updated status
      const newStatus = await getCompetitionStatus();
      
      // Update refs before calling onStatusChange to prevent loops
      lastIsRunningRef.current = newStatus?.is_running || false;
      
      // Update status in parent (this will trigger re-render)
      onStatusChange(newStatus);
      
      // Manually set step to 3 after a short delay to ensure state is settled
      // This prevents the useEffect from causing loops
      setTimeout(() => {
        if (newStatus?.is_running) {
          setCurrentStep(3);
        }
      }, 100);
      
    } catch (err) {
      const errorMessage = err.message || "Failed to start trading";
      setError(errorMessage);
      console.error("Error starting trading:", err);
      // Don't change step on error - stay on Step 2
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Continue/Pause Trading
  const handleContinueTrading = async () => {
    try {
      setLoading(true);
      setError(null);
      await resumeCompetition();
      const newStatus = await getCompetitionStatus();
      onStatusChange(newStatus);
    } catch (err) {
      setError(err.message || "Failed to continue trading");
      console.error("Error continuing trading:", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePauseTrading = async () => {
    try {
      setLoading(true);
      setError(null);
      await pauseCompetition();
      const newStatus = await getCompetitionStatus();
      onStatusChange(newStatus);
    } catch (err) {
      setError(err.message || "Failed to pause trading");
      console.error("Error pausing trading:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRestartFromTrading = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to restart? This will reset all accounts and clear all trading history. You will need to generate a new strategy report."
    );
    
    if (!confirmed) return;

    try {
      setLoading(true);
      setError(null);
      // Reset competition state
      await startCompetition();
      const newStatus = await getCompetitionStatus();
      onStatusChange(newStatus);
      // Clear strategy and go to step 2
      setStrategy(null);
      setCurrentStep(2);
    } catch (err) {
      setError(err.message || "Failed to restart competition");
      console.error("Error restarting competition:", err);
    } finally {
      setLoading(false);
    }
  };

  // Render step content based on current step
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <StepContent
            actions={
              <button
                onClick={handleStartCompetition}
                disabled={loading}
                className="btn-primary competition-btn"
              >
                {loading ? "Starting..." : "Start Competition"}
              </button>
            }
          />
        );

      case 2:
        return (
          <StepContent
            actions={
              !strategy ? (
                <button
                  onClick={() => handleGenerateStrategy(false)}
                  disabled={generatingStrategy}
                  className="btn-primary competition-btn"
                >
                  {generatingStrategy ? "Generating..." : "Generate Strategy Report"}
                </button>
              ) : (
                <>
                  <button
                    onClick={() => handleGenerateStrategy(true)}
                    disabled={generatingStrategy}
                    className="btn-secondary competition-btn"
                  >
                    {generatingStrategy ? "Regenerating..." : "Regenerate Strategy Report"}
                  </button>
                  <button
                    onClick={handleStartTrading}
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
                    rows={15}
                  />
                </div>
              ) : null}
            </div>
          </StepContent>
        );

      case 3:
        return (
          <StepContent
            actions={
              <>
                {is_paused ? (
                  <button
                    onClick={handleContinueTrading}
                    disabled={loading}
                    className="btn-primary competition-btn"
                  >
                    {loading ? "Continuing..." : "▶️ Continue Trading"}
                  </button>
                ) : (
                  <button
                    onClick={handlePauseTrading}
                    disabled={loading}
                    className="btn-secondary competition-btn"
                  >
                    {loading ? "Pausing..." : "⏸️ Pause Trading"}
                  </button>
                )}
                <button
                  onClick={handleRestartFromTrading}
                  className="btn-secondary competition-btn"
                >
                  Restart Competition
                </button>
              </>
            }
          />
        );

      default:
        return null;
    }
  };

  if (!competitionStatus) {
    return null;
  }

  // Get status display
  const getStatusDisplay = () => {
    if (is_running && !is_paused) {
      return { class: "running", text: "🟢 Competition Running" };
    }
    if (is_paused) {
      return { class: "paused", text: "⏸️ Competition Paused" };
    }
    return { class: "stopped", text: "⚪ Competition Stopped" };
  };

  const statusDisplay = getStatusDisplay();

  return (
    <div className="competition-flow">
      <div className="competition-flow-header">
        <h2 className="section-title">Competition Control</h2>
        <div className="competition-status-display">
          <span className={`status-badge ${statusDisplay.class}`}>
            {statusDisplay.text}
          </span>
        </div>
      </div>

      {error && (
        <div className="error competition-error">
          {error}
        </div>
      )}

      {renderStepContent()}
    </div>
  );
};

export default CompetitionFlow;
