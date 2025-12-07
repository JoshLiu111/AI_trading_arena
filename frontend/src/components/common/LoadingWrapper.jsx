import Spinner from "./Spinner";

/**
 * Unified loading and error wrapper component
 * Eliminates repeated loading/error handling patterns
 */
const LoadingWrapper = ({ 
  loading, 
  error, 
  children,
  // Customization options
  loadingComponent = null,
  errorComponent = null,
  containerClass = "",
  showBackLink = false,
  backLinkTo = "/dashboard",
  backLinkText = "🔙 Back to Dashboard",
}) => {
  if (loading) {
    return loadingComponent || (
      <div className="spinner-container">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return errorComponent || (
      <div className={containerClass || "error-container"}>
        <div className="error">❌ Error: {error}</div>
        {showBackLink && (
          <a href={backLinkTo} className="back-link">
            {backLinkText}
          </a>
        )}
      </div>
    );
  }

  return children;
};

export default LoadingWrapper;
