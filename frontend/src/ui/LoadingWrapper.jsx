import { Link } from "react-router-dom";
import Spinner from "./Spinner";

/**
 * Loading Wrapper Component
 * Wraps content with loading and error states
 */
const LoadingWrapper = ({
  loading,
  error,
  children,
  showBackLink = false,
  containerClass = "",
}) => {
  if (loading) {
    return (
      <div className={`spinner-container ${containerClass}`}>
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className={`error-container ${containerClass}`}>
        {showBackLink && (
          <Link to="/dashboard" className="back-link">
            🔙 Back to Dashboard
          </Link>
        )}
        <div className="error">
          ❌ Error: {error}
        </div>
      </div>
    );
  }

  return <div className={containerClass}>{children}</div>;
};

export default LoadingWrapper;

