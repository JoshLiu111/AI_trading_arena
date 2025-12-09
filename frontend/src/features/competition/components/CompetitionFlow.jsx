import { useCompetition } from "../hooks/useCompetition";
import CompetitionStatusBadge from "./CompetitionStatusBadge";
import CompetitionStepWrapper from "./CompetitionStepWrapper";
import StrategyGenerationStep from "./StrategyGenerationStep";
import TradingControlsStep from "./TradingControlsStep";

/**
 * CompetitionFlow Component
 * Main component for managing competition flow through different steps
 * 
 * @param {Object} props
 * @param {Object|null} props.competitionStatus - Initial competition status object
 * @param {Function} props.onStatusChange - Callback function called when competition status changes
 * @param {Array} props.accounts - Array of account objects
 */
const CompetitionFlow = ({ competitionStatus: initialCompetitionStatus, onStatusChange, accounts }) => {
  const {
    competitionStatus,
    currentStep,
    strategy,
    generatingStrategy,
    loading,
    error,
    is_running,
    is_paused,
    handleStartCompetition,
    handleRestartCompetition,
    handleGenerateStrategy,
    handleStartTrading,
    handleContinueTrading,
    handlePauseTrading,
    handleRestartFromTrading,
  } = useCompetition({
    initialCompetitionStatus,
    onStatusChange,
    accounts,
  });

  // Render step content based on current step
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <CompetitionStepWrapper
            actions={
              <button
                onClick={handleStartCompetition}
                className="btn-primary competition-btn"
              >
                Start Competition
              </button>
            }
          />
        );

      case 2:
        return (
          <StrategyGenerationStep
            strategy={strategy}
            loading={loading}
            generatingStrategy={generatingStrategy}
            onGenerate={() => handleGenerateStrategy(false)}
            onRegenerate={() => handleGenerateStrategy(true)}
            onStartTrading={handleStartTrading}
          />
        );

      case 3:
        return (
          <TradingControlsStep
            is_paused={is_paused}
            loading={loading}
            onPause={handlePauseTrading}
            onContinue={handleContinueTrading}
            onRestart={handleRestartFromTrading}
          />
        );

      default:
        return null;
    }
  };

  if (!competitionStatus) {
    return null;
  }

  return (
    <div className="competition-flow">
      <div className="competition-flow-header">
        <h2 className="section-title">Competition Control</h2>
        <CompetitionStatusBadge is_running={is_running} is_paused={is_paused} />
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
