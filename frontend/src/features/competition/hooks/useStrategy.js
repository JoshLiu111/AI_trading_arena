import { useState, useEffect, useRef } from "react";
import { getLatestStrategy } from "@/lib/api";
import { formatStrategyContent } from "@/lib/utils";
import { ACCOUNT_TYPES, API_DEFAULTS } from "@/lib/constants";
import { COMPETITION_CONSTANTS } from "../constants/competition";
import * as competitionService from "../services/competitionService";

/**
 * Hook for managing strategy state and operations
 * Handles strategy loading, generation, and auto-loading
 * 
 * @param {Object} options
 * @param {number} options.currentStep - Current step number
 * @param {number} options.aiAccountId - AI account ID for strategy operations
 * @returns {Object} Strategy state and handlers
 */
export function useStrategy({ currentStep, aiAccountId }) {
  const [strategy, setStrategy] = useState(null);
  const [generatingStrategy, setGeneratingStrategy] = useState(false);
  const isAutoLoadingRef = useRef(false);

  // Auto-load strategy when in Step 2 and strategy is not loaded
  useEffect(() => {
    // Only auto-load if we're in Step 2, no strategy loaded, not currently generating, and not already loading
    if (
      currentStep === COMPETITION_CONSTANTS.STEPS.STRATEGY &&
      !strategy &&
      !generatingStrategy &&
      !isAutoLoadingRef.current &&
      aiAccountId
    ) {
      isAutoLoadingRef.current = true;
      
      const loadStrategyIfNeeded = async () => {
        try {
          const strategyData = await getLatestStrategy(aiAccountId);
          
          // Format strategy for display
          const strategyText = formatStrategyContent(strategyData);
          
          if (strategyText && strategyText !== "No strategy report available.") {
            setStrategy(strategyText);
          } else {
            // No strategy available, don't set it
            isAutoLoadingRef.current = false;
            return;
          }
        } catch (err) {
          // Silently fail - strategy might not exist yet
        } finally {
          // Reset flag after a delay to allow state to settle
          setTimeout(() => {
            isAutoLoadingRef.current = false;
          }, COMPETITION_CONSTANTS.AUTO_LOAD_DELAY);
        }
      };

      loadStrategyIfNeeded();
    }
  }, [currentStep, strategy, generatingStrategy, aiAccountId]);

  /**
   * Generate or regenerate strategy
   * @param {boolean} isRegenerate - Whether to regenerate existing strategy
   */
  const generateStrategy = async (isRegenerate = false) => {
    try {
      setGeneratingStrategy(true);
      
      const result = await competitionService.generateStrategy(aiAccountId, isRegenerate);
      
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

  /**
   * Clear strategy
   */
  const clearStrategy = () => {
    setStrategy(null);
    isAutoLoadingRef.current = false;
  };

  /**
   * Reset auto-loading flag
   */
  const resetAutoLoading = () => {
    isAutoLoadingRef.current = false;
  };

  return {
    strategy,
    generatingStrategy,
    generateStrategy,
    clearStrategy,
    resetAutoLoading,
  };
}

