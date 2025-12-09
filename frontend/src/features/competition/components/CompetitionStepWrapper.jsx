/**
 * Competition Step Wrapper Component
 * Provides consistent layout for competition flow steps
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to display in the step
 * @param {React.ReactNode} props.actions - Action buttons for the step
 */
const CompetitionStepWrapper = ({ children, actions }) => (
  <div className="step-content">
    {children}
    <div className="step-actions-centered">
      {actions}
    </div>
  </div>
);

export default CompetitionStepWrapper;
