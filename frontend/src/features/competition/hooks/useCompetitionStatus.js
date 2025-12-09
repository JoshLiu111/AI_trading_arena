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

    // Initial fetch only if status is not provided
    if (!competitionStatus) {
      fetchStatus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount - onStatusChange is intentionally excluded to prevent loops

  // Update internal status when prop changes
  useEffect(() => {
    if (initialCompetitionStatus) {
      setCompetitionStatus(initialCompetitionStatus);
    }
  }, [initialCompetitionStatus]);

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

