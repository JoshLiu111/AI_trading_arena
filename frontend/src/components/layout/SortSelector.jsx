import { SORT_OPTIONS, SORT_LABELS } from "../../constants";

const SortSelector = ({ sortBy, onSortChange }) => {
  return (
    <div className="controls">
      <label htmlFor="sort">Sort By:</label>
      <select
        id="sort"
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value)}
      >
        {Object.entries(SORT_OPTIONS).map(([key, value]) => (
          <option key={value} value={value}>
            {SORT_LABELS[value]}
          </option>
        ))}
      </select>
    </div>
  );
};

export default SortSelector;
