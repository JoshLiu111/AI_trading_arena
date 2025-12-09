import { useState, useEffect } from "react";
import { getCompetitionStatus } from "@/lib/api";

/**
 * Hook for managing competition status
 * Handles fetching and syncing competition status
 * 
 * @param {Object} options
 * @param {Object|null} options.initialCompetitionStatus - Initial competition status
 * @param {Function} options.onStatusChange - Callback when status changes
 * @returns {Object} Competition status state and utilities
 */
export function useCompetitionStatus({ initialCompetitionStatus, onStatusChange }) {
  const [competitionStatus, setCompetitionStatus] = useState(initialCompetitionStatus);

  // Fetch competition status on mount if not provided
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getCompetitionStatus();
        setCompetitionStatus(status);
        if (onStatusChange) {
          onStatusChange(status);
        }
      } catch (err) {
        console.error("Error fetching competition status:", err);
      }
    };

    // Always fetch status on mount to ensure we have the latest state
    // This prevents stale state when navigating back to the page
    fetchStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount - onStatusChange is intentionally excluded to prevent loops

  // Update internal status when prop changes (but only if it's different to avoid unnecessary updates)
  useEffect(() => {
    if (initialCompetitionStatus) {
      // Only update if the status actually changed to prevent loops
      const currentIsRunning = competitionStatus?.is_running || false;
      const currentIsPaused = competitionStatus?.is_paused || false;
      const newIsRunning = initialCompetitionStatus?.is_running || false;
      const newIsPaused = initialCompetitionStatus?.is_paused || false;
      
      if (currentIsRunning !== newIsRunning || currentIsPaused !== newIsPaused) {
        setCompetitionStatus(initialCompetitionStatus);
      }
    } else if (competitionStatus && !initialCompetitionStatus) {
      // If prop becomes null but we have state, keep the state (don't reset to null)
      // This prevents losing state when parent component re-renders
    }
  }, [initialCompetitionStatus, competitionStatus]);

  /**
   * Update competition status
   * @param {Object} newStatus - New competition status
   */
  const updateStatus = (newStatus) => {
    setCompetitionStatus(newStatus);
    if (onStatusChange) {
      onStatusChange(newStatus);
    }
  };

  return {
    competitionStatus,
    setCompetitionStatus: updateStatus,
    is_running: competitionStatus?.is_running || false,
    is_paused: competitionStatus?.is_paused || false,
  };
}

