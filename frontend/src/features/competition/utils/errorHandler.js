/**
 * Unified error handling utility for competition module
 * 
 * @param {Error|Object|string} error - Error object, error response, or error message
 * @param {Function} setError - State setter for error message
 * @param {string} defaultMessage - Default error message if error doesn't have a message
 */
export function handleCompetitionError(error, setError, defaultMessage = "An unexpected error occurred") {
  let errorMessage = defaultMessage;
  
  if (typeof error === "string") {
    errorMessage = error;
  } else if (error?.message) {
    errorMessage = error.message;
  } else if (error?.error) {
    errorMessage = error.error;
  }
  
  setError(errorMessage);
  console.error("Competition error:", error);
}

