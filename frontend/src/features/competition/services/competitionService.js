/**
 * Competition Service
 * Business logic for competition management (strategy generation, start trading, pause/continue/restart)
 */

import { 
  generateStrategy as generateStrategyAPI,
  regenerateStrategy as regenerateStrategyAPI,
  getLatestStrategy,
  startCompetition,
  pauseCompetition,
  resumeCompetition,
  getCompetitionStatus
} from "@/lib/api";
import { formatStrategyContent } from "@/lib/utils";
import { API_DEFAULTS } from "@/lib/constants";
import { COMPETITION_CONSTANTS } from "../constants/competition";

/**
 * Generate or regenerate strategy
 */
export async function generateStrategy(aiAccountId, isRegenerate = false) {
  const accountId = aiAccountId || API_DEFAULTS.DEFAULT_AI_ACCOUNT_ID;
  
  try {
    if (isRegenerate) {
      await regenerateStrategyAPI(accountId);
      await new Promise((resolve) => setTimeout(resolve, COMPETITION_CONSTANTS.STRATEGY_LOAD_DELAY));
    } else {
      await generateStrategyAPI(accountId);
      await new Promise((resolve) => setTimeout(resolve, COMPETITION_CONSTANTS.STRATEGY_LOAD_DELAY));
    }
    
    // Fetch the generated strategy
    const strategyData = await getLatestStrategy(accountId);
    
    // Format strategy for display
    const strategyText = formatStrategyContent(strategyData);
    
    return { success: true, strategy: strategyText };
  } catch (err) {
    const errorMessage = err.message || (isRegenerate ? "Failed to regenerate strategy" : "Failed to generate strategy");
    console.error("Error generating strategy:", err);
    return { success: false, error: errorMessage };
  }
}

/**
 * Start trading (start competition)
 */
export async function startTrading() {
  try {
    const result = await startCompetition();
    const newStatus = await getCompetitionStatus();
    return { success: true, status: newStatus };
  } catch (err) {
    const errorMessage = err.message || "Failed to start trading";
    console.error("Error starting trading:", err);
    return { success: false, error: errorMessage };
  }
}

/**
 * Pause competition
 */
export async function pauseCompetitionService() {
  try {
    await pauseCompetition();
    const newStatus = await getCompetitionStatus();
    return { success: true, status: newStatus };
  } catch (err) {
    const errorMessage = err.message || "Failed to pause trading";
    console.error("Error pausing trading:", err);
    return { success: false, error: errorMessage };
  }
}

/**
 * Resume/Continue competition
 */
export async function resumeCompetitionService() {
  try {
    await resumeCompetition();
    const newStatus = await getCompetitionStatus();
    return { success: true, status: newStatus };
  } catch (err) {
    const errorMessage = err.message || "Failed to continue trading";
    console.error("Error continuing trading:", err);
    return { success: false, error: errorMessage };
  }
}

/**
 * Restart competition
 */
export async function restartCompetition() {
  const confirmed = window.confirm(
    "Are you sure you want to restart? This will reset all accounts and clear all trading history. You will need to generate a new strategy report."
  );
  
  if (!confirmed) {
    return { success: false, cancelled: true };
  }

  try {
    await startCompetition();
    const newStatus = await getCompetitionStatus();
    return { success: true, status: newStatus };
  } catch (err) {
    const errorMessage = err.message || "Failed to restart competition";
    console.error("Error restarting competition:", err);
    return { success: false, error: errorMessage };
  }
}

