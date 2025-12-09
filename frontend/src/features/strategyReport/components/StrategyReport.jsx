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
      // Only fetch if is_running actually changed
      if (lastIsRunningRef.current === competitionStatus?.is_running) {
        return; // No change, skip
      }
      
      lastIsRunningRef.current = competitionStatus?.is_running;
      
      if (!competitionStatus?.is_running) {
        setStrategyReport(null);
        return;
      }
      
      if (aiAccountId) {
        try {
          const strategyData = await getLatestStrategy(aiAccountId);
          const strategyText = formatStrategyContent(strategyData);
          setStrategyReport(strategyText);
        } catch (err) {
          console.error("Error fetching AI strategy report:", err);
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

