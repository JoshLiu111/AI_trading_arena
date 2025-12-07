/**
 * Loading spinner component
 */
const Spinner = ({ size = "default", label = "Loading..." }) => {
  const sizeClass = size === "small" ? "spinner-small" : "";
  
  return (
    <div className={`spinner-container ${sizeClass}`}>
      <div className="spinner" aria-label={label}></div>
    </div>
  );
};

export default Spinner;
