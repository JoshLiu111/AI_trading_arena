import { useState, useEffect, useRef } from "react";
import { getLatestStrategy } from "@/lib/api";
import { formatStrategyContent } from "@/lib/utils";
import { ACCOUNT_TYPES, API_DEFAULTS } from "@/lib/constants";
import { COMPETITION_CONSTANTS } from "../constants/competition";
import { handleCompetitionError } from "../utils/errorHandler";
import * as competitionService from "../services/competitionService";
import { useCompetitionStatus } from "./useCompetitionStatus";
import { useCompetitionSteps } from "./useCompetitionSteps";

/**
 * Main competition management hook (composite hook)
 * Combines status, steps, and strategy management
 * 
 * @param {Object} options - Competition configuration
 * @param {Object|null} options.initialCompetitionStatus - Initial competition status
 * @param {Function} options.onStatusChange - Callback when status changes
 * @param {Array} options.accounts - List of accounts
 * @returns {Object} Competition state and handlers
 */
export function useCompetition({ 
  initialCompetitionStatus, 
  onStatusChange, 
  accounts 
}) {
  // Get AI account ID
  const aiAccountId = useRef(null);
  useEffect(() => {
    if (accounts && Array.isArray(accounts)) {
      const aiAccount = accounts.find(acc => acc?.account_type === ACCOUNT_TYPES.AI);
      aiAccountId.current = aiAccount?.id || API_DEFAULTS.DEFAULT_AI_ACCOUNT_ID;
    } else {
      aiAccountId.current = API_DEFAULTS.DEFAULT_AI_ACCOUNT_ID;
    }
  }, [accounts]);

  // Local state for operations
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Use status hook
  const {
    competitionStatus,
    setCompetitionStatus,
    is_running,
    is_paused,
  } = useCompetitionStatus({
    initialCompetitionStatus,
    onStatusChange,
  });

  // Strategy state (managed locally to avoid circular dependency with steps)
  const [strategy, setStrategy] = useState(null);
  const [generatingStrategy, setGeneratingStrategy] = useState(false);
  const isAutoLoadingRef = useRef(false);

  // Use steps hook (needs strategy)
  const {
    currentStep,
    setCurrentStep,
    getRefs,
  } = useCompetitionSteps({
    is_running,
    strategy,
    loading,
  });

  // Auto-load strategy when in Step 2
  useEffect(() => {
    if (
      currentStep === COMPETITION_CONSTANTS.STEPS.STRATEGY &&
      !strategy &&
      !generatingStrategy &&
      !isAutoLoadingRef.current &&
      aiAccountId.current
    ) {
      isAutoLoadingRef.current = true;
      
      const loadStrategyIfNeeded = async () => {
        try {
          const strategyData = await getLatestStrategy(aiAccountId.current);
          const strategyText = formatStrategyContent(strategyData);
          
          if (strategyText && strategyText !== "No strategy report available.") {
            setStrategy(strategyText);
          }
        } catch (err) {
          // Strategy not available yet
        } finally {
          setTimeout(() => {
            isAutoLoadingRef.current = false;
          }, COMPETITION_CONSTANTS.AUTO_LOAD_DELAY);
        }
      };

      loadStrategyIfNeeded();
    }
  }, [currentStep, strategy, generatingStrategy]);

  // Generate strategy handler
  const generateStrategyInternal = async (isRegenerate = false) => {
    try {
      setGeneratingStrategy(true);
      
      const result = await competitionService.generateStrategy(aiAccountId.current, isRegenerate);
      
      if (result.success && result.strategy) {
        setStrategy(result.strategy);
        return { success: true };
      } else {
        return { success: false, error: result.error || "Failed to generate strategy" };
      }
    } catch (err) {
      return { success: false, error: err.message || "Failed to generate strategy" };
    } finally {
      setGeneratingStrategy(false);
    }
  };

  // Clear strategy
  const clearStrategy = () => {
    setStrategy(null);
    isAutoLoadingRef.current = false;
  };

  // Reset auto-loading
  const resetAutoLoading = () => {
    isAutoLoadingRef.current = false;
  };

  // Step 1: Start Competition - Actually start the competition (initialize data)
  const handleStartCompetition = async () => {
    try {
      setLoading(true);
      setError(null);
      resetAutoLoading();
      clearStrategy();
      
      // Actually start the competition (this will create accounts, refresh stock data, etc.)
      // Use startTrading which calls startCompetition API without confirmation dialog
      const result = await competitionService.startTrading();
      
      if (result.success && result.status) {
        setCompetitionStatus(result.status);
        // Navigate to step 2 after competition is started
        setCurrentStep(COMPETITION_CONSTANTS.STEPS.STRATEGY);
      } else {
        handleCompetitionError(
          result.error || "Failed to start competition",
          setError,
          "Failed to start competition"
        );
      }
    } catch (err) {
      handleCompetitionError(err, setError, "Failed to start competition");
    } finally {
      setLoading(false);
    }
  };

  // Restart Competition
  const handleRestartCompetition = async () => {
    try {
      setError(null);
      const result = await competitionService.restartCompetition();
      
      if (result.cancelled) {
        return; // User cancelled
      }
      
      if (result.success && result.status) {
        setCompetitionStatus(result.status);
        clearStrategy();
        setCurrentStep(COMPETITION_CONSTANTS.STEPS.STRATEGY);
      } else {
        handleCompetitionError(
          result.error || "Failed to restart competition",
          setError,
          "Failed to restart competition"
        );
      }
    } catch (err) {
      handleCompetitionError(err, setError, "Failed to restart competition");
    }
  };

  // Step 2: Generate Strategy
  const handleGenerateStrategy = async (isRegenerate = false) => {
    const result = await generateStrategyInternal(isRegenerate);
    if (!result.success) {
      handleCompetitionError(
        result.error || "Failed to generate strategy",
        setError,
        "Failed to generate strategy"
      );
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
      
      const result = await competitionService.startTrading();
      
      if (result.success && result.status) {
        // Update refs before calling onStatusChange to prevent loops
        const { lastIsRunningRef } = getRefs();
        lastIsRunningRef.current = result.status?.is_running || false;
        
        // Update internal status
        setCompetitionStatus(result.status);
        
        // Manually set step to 3 after a short delay
        setCurrentStep(COMPETITION_CONSTANTS.STEPS.TRADING, COMPETITION_CONSTANTS.STEP_DELAY);
      } else {
        handleCompetitionError(
          result.error || "Failed to start trading",
          setError,
          "Failed to start trading"
        );
      }
    } catch (err) {
      handleCompetitionError(err, setError, "Failed to start trading");
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Continue Trading
  const handleContinueTrading = async () => {
    try {
      setError(null);
      const result = await competitionService.resumeCompetitionService();
      
      if (result.success && result.status) {
        setCompetitionStatus(result.status);
      } else {
        handleCompetitionError(
          result.error || "Failed to continue trading",
          setError,
          "Failed to continue trading"
        );
      }
    } catch (err) {
      handleCompetitionError(err, setError, "Failed to continue trading");
    }
  };

  // Step 3: Pause Trading
  const handlePauseTrading = async () => {
    try {
      setError(null);
      const result = await competitionService.pauseCompetitionService();
      
      if (result.success && result.status) {
        setCompetitionStatus(result.status);
      } else {
        handleCompetitionError(
          result.error || "Failed to pause trading",
          setError,
          "Failed to pause trading"
        );
      }
    } catch (err) {
      handleCompetitionError(err, setError, "Failed to pause trading");
    }
  };

  // Step 3: Restart from Trading
  const handleRestartFromTrading = async () => {
    try {
      setError(null);
      const result = await competitionService.restartCompetition();
      
      if (result.cancelled) {
        return; // User cancelled
      }
      
      if (result.success && result.status) {
        setCompetitionStatus(result.status);
        clearStrategy();
        setCurrentStep(COMPETITION_CONSTANTS.STEPS.STRATEGY);
      } else {
        handleCompetitionError(
          result.error || "Failed to restart competition",
          setError,
          "Failed to restart competition"
        );
      }
    } catch (err) {
      handleCompetitionError(err, setError, "Failed to restart competition");
    }
  };

  return {
    // State
    competitionStatus,
    currentStep,
    strategy,
    generatingStrategy,
    loading,
    error,
    is_running,
    is_paused,
    // Handlers
    handleStartCompetition,
    handleRestartCompetition,
    handleGenerateStrategy,
    handleStartTrading,
    handleContinueTrading,
    handlePauseTrading,
    handleRestartFromTrading,
  };
}
