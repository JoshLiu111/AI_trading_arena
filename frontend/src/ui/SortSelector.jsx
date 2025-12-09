import { SORT_OPTIONS, SORT_LABELS } from "@/lib/constants";

/**
 * Sort Selector Component
 * Dropdown for sorting stocks
 */
const SortSelector = ({ sortBy, onSortChange }) => {
  return (
    <div className="controls">
      <label htmlFor="sort-select">Sort by:</label>
      <select
        id="sort-select"
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value)}
      >
        <option value={SORT_OPTIONS.PRICE_DESC}>{SORT_LABELS[SORT_OPTIONS.PRICE_DESC]}</option>
        <option value={SORT_OPTIONS.PRICE_ASC}>{SORT_LABELS[SORT_OPTIONS.PRICE_ASC]}</option>
        <option value={SORT_OPTIONS.CHANGE_DESC}>{SORT_LABELS[SORT_OPTIONS.CHANGE_DESC]}</option>
        <option value={SORT_OPTIONS.CHANGE_ASC}>{SORT_LABELS[SORT_OPTIONS.CHANGE_ASC]}</option>
      </select>
    </div>
  );
};

export default SortSelector;

