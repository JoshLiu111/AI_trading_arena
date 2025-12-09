import { useState, useEffect, useRef, useMemo } from "react";
import { getLatestStrategy } from "@/lib/api";
import { formatStrategyContent } from "@/lib/utils";
import { ACCOUNT_TYPES, API_DEFAULTS } from "@/lib/constants";

/**
 * Strategy Report Component
 * Fetches and displays AI strategy report when competition is running
 * 
 * @param {Object} props
 * @param {Object|null} props.competitionStatus - Competition status object
 * @param {Array} props.accounts - Array of account objects
 */
const StrategyReport = ({ competitionStatus, accounts }) => {
  const [strategyReport, setStrategyReport] = useState(null);
  const lastIsRunningRef = useRef(null);

  // Memoize AI account ID to avoid unnecessary recalculations
  const aiAccountId = useMemo(() => {
    if (!accounts || !Array.isArray(accounts)) {
      return API_DEFAULTS.DEFAULT_AI_ACCOUNT_ID;
    }
    const aiAccount = accounts.find(acc => acc.account_type === ACCOUNT_TYPES.AI);
    return aiAccount?.id || API_DEFAULTS.DEFAULT_AI_ACCOUNT_ID;
  }, [accounts]);

  // Fetch AI strategy report when competition is running
  useEffect(() => {
    const fetchAiStrategyReport = async () => {
      // Check if is_running actually changed or if this is the first mount
      const currentIsRunning = competitionStatus?.is_running || false;
      const prevIsRunning = lastIsRunningRef.current;
      
      // If competition is not running, clear the report
      if (!currentIsRunning) {
        setStrategyReport(null);
        // Update ref to track current state
        lastIsRunningRef.current = currentIsRunning;
        return;
      }
      
      // Fetch strategy if:
      // 1. This is the first mount (prevIsRunning is null/undefined) and competition is running, OR
      // 2. is_running changed from false to true
      const shouldFetch = 
        (prevIsRunning === null || prevIsRunning === undefined) ||
        (prevIsRunning !== currentIsRunning && currentIsRunning);
      
      // Update ref to track current state
      lastIsRunningRef.current = currentIsRunning;
      
      if (shouldFetch && aiAccountId) {
        try {
          const strategyData = await getLatestStrategy(aiAccountId);
          const strategyText = formatStrategyContent(strategyData);
          setStrategyReport(strategyText);
        } catch (err) {
          console.error("Error fetching AI strategy report:", err);
          setStrategyReport(null);
        }
      }
    };

    fetchAiStrategyReport();
  }, [competitionStatus?.is_running, aiAccountId]);

  // Don't render if competition is not running or no strategy report
  if (!competitionStatus?.is_running || !strategyReport) {
    return null;
  }

  return (
    <section className="dashboard-section">
      <div className="ai-strategy-report">
        <h2 className="section-title">AI Strategy Report</h2>
        <div className="strategy-report-content">
          <pre className="strategy-report-text">{strategyReport}</pre>
        </div>
      </div>
    </section>
  );
};

export default StrategyReport;

