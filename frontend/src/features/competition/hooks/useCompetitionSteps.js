import { useState, useEffect, useRef } from "react";
import { COMPETITION_CONSTANTS } from "../constants/competition";

/**
 * Hook for managing competition flow steps
 * Handles step transitions and synchronization with competition status
 * 
 * @param {Object} options
 * @param {boolean} options.is_running - Whether competition is running
 * @param {string|null} options.strategy - Current strategy text
 * @param {boolean} options.loading - Whether an operation is in progress
 * @returns {Object} Step state and utilities
 */
export function useCompetitionSteps({ is_running, strategy, loading }) {
  // Initialize step based on is_running status to handle remounting correctly
  const getInitialStep = (isRunning, hasStrategy) => {
    if (isRunning) {
      return COMPETITION_CONSTANTS.STEPS.TRADING;
    } else if (hasStrategy) {
      return COMPETITION_CONSTANTS.STEPS.STRATEGY;
    } else {
      return COMPETITION_CONSTANTS.STEPS.START;
    }
  };
  
  const [currentStep, setCurrentStep] = useState(() => getInitialStep(is_running, !!strategy));
  
  // Use refs to prevent infinite loops
  const lastIsRunningRef = useRef(is_running);
  const lastStrategyRef = useRef(strategy);
  const isInitializedRef = useRef(false);

  // Sync currentStep with competition status (only when status actually changes)
  useEffect(() => {
    // On first mount, initialize refs and step
    if (!isInitializedRef.current) {
      lastIsRunningRef.current = is_running;
      lastStrategyRef.current = strategy;
      isInitializedRef.current = true;
      
      // Set initial step based on current state
      const initialStep = getInitialStep(is_running, !!strategy);
      setCurrentStep(initialStep);
      return;
    }
    
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
      setCurrentStep(COMPETITION_CONSTANTS.STEPS.TRADING);
    } else if (!is_running && strategy && !prevStrategy) {
      // Strategy just loaded and competition not running - go to Step 2
      setCurrentStep(COMPETITION_CONSTANTS.STEPS.STRATEGY);
    } else if (!is_running && !strategy && prevStrategy) {
      // Strategy was cleared - go to Step 1
      setCurrentStep(COMPETITION_CONSTANTS.STEPS.START);
    }
    // Don't change step if just strategy content changed but competition is running
  }, [is_running, strategy, loading]);

  /**
   * Manually set step (with optional delay)
   * @param {number} step - Step number to set
   * @param {number} delay - Optional delay in milliseconds
   */
  const setStep = (step, delay = 0) => {
    if (delay > 0) {
      setTimeout(() => {
        setCurrentStep(step);
      }, delay);
    } else {
      setCurrentStep(step);
    }
  };

  /**
   * Get refs for external use (to prevent loops)
   */
  const getRefs = () => ({
    lastIsRunningRef,
    lastStrategyRef,
  });

  return {
    currentStep,
    setCurrentStep: setStep,
    getRefs,
  };
}
