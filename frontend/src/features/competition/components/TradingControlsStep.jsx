import CompetitionStepWrapper from "./CompetitionStepWrapper";

/**
 * Trading Controls Step Component
 * Handles trading controls (pause/continue/restart)
 * 
 * @param {Object} props
 * @param {boolean} props.is_paused - Whether the competition is paused
 * @param {boolean} props.loading - Whether an operation is in progress
 * @param {Function} props.onPause - Callback to pause trading
 * @param {Function} props.onContinue - Callback to continue trading
 * @param {Function} props.onRestart - Callback to restart competition
 */
const TradingControlsStep = ({
  is_paused,
  loading,
  onPause,
  onContinue,
  onRestart,
}) => {
  return (
    <CompetitionStepWrapper
      actions={
        <>
          {is_paused ? (
            <button
              onClick={onContinue}
              disabled={loading}
              className="btn-primary competition-btn"
            >
              {loading ? "Continuing..." : "▶️ Continue Trading"}
            </button>
          ) : (
            <button
              onClick={onPause}
              disabled={loading}
              className="btn-secondary competition-btn"
            >
              {loading ? "Pausing..." : "⏸️ Pause Trading"}
            </button>
          )}
          <button
            onClick={onRestart}
            className="btn-secondary competition-btn"
          >
            Restart Competition
          </button>
        </>
      }
    />
  );
};

export default TradingControlsStep;
