/**
 * Competition Status Badge Component
 * Displays the current competition status (Running/Paused/Stopped)
 * 
 * @param {Object} props
 * @param {boolean} props.is_running - Whether the competition is currently running
 * @param {boolean} props.is_paused - Whether the competition is currently paused
 */
const CompetitionStatusBadge = ({ is_running, is_paused }) => {
  const getStatusDisplay = () => {
    if (is_running && !is_paused) {
      return { class: "running", text: "🟢 Competition Running" };
    }
    if (is_paused) {
      return { class: "paused", text: "⏸️ Competition Paused" };
    }
    return { class: "stopped", text: "⚪ Competition Stopped" };
  };

  const statusDisplay = getStatusDisplay();

  return (
    <div className="competition-status-display">
      <span className={`status-badge ${statusDisplay.class}`}>
        {statusDisplay.text}
      </span>
    </div>
  );
};

export default CompetitionStatusBadge;

