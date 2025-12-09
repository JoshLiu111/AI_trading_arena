/**
 * Filter Input Component
 * Input field for filtering stocks
 */
const FilterInput = ({ filter, onFilterChange }) => {
  return (
    <div className="filter">
      <input
        type="text"
        placeholder="Filter by ticker or name..."
        value={filter}
        onChange={(e) => onFilterChange(e.target.value)}
      />
    </div>
  );
};

export default FilterInput;

