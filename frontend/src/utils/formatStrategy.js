/**
 * Format strategy content from backend to readable text
 * Backend format: { summary, actions: [{ticker, action, quantity, rationale}], selected_stocks }
 * Supports both formats:
 * - New: { content: {...}, selected_stocks: [...] }
 * - Old: { strategy_content: "...", selected_stocks: "..." }
 */
export const formatStrategyContent = (strategyData) => {
  if (!strategyData) {
    return "No strategy report available.";
  }

  // Handle case where strategy is null
  if (strategyData.strategy === null) {
    return "No strategy report available.";
  }

  // Get content and selected_stocks from different possible formats
  let content = strategyData.content || strategyData.strategy_content;
  let selectedStocks = strategyData.selected_stocks || [];

  // If content is not available, return early
  if (!content) {
    return "No strategy report available.";
  }

  // Parse content if it's a string
  let parsed;
  if (typeof content === 'string') {
    try {
      parsed = JSON.parse(content);
    } catch {
      // If not JSON, use as plain text
      return content;
    }
  } else {
    // content is already an object
    parsed = content;
  }

  let strategyText = "";
  
  // Format according to backend structure
  if (parsed.summary) {
    strategyText = parsed.summary;
  }
  
  // Add actions if available
  if (parsed.actions && Array.isArray(parsed.actions) && parsed.actions.length > 0) {
    if (!strategyText) {
      strategyText = "Trading strategy generated based on current market conditions.";
    }
    strategyText += "\n\nRecommended Actions:\n";
    parsed.actions.forEach((action, index) => {
      strategyText += `${index + 1}. ${action.action} ${action.quantity} shares of ${action.ticker}\n`;
      if (action.rationale) {
        strategyText += `   Reason: ${action.rationale}\n`;
      }
    });
  }
  
  // Add selected stocks if available
  // selected_stocks might be array or string
  let stocksArray = [];
  if (Array.isArray(selectedStocks)) {
    stocksArray = selectedStocks;
  } else if (typeof selectedStocks === 'string') {
    // Try to parse as JSON first, then fallback to comma-separated
    try {
      const parsedStocks = JSON.parse(selectedStocks);
      stocksArray = Array.isArray(parsedStocks) ? parsedStocks : [];
    } catch {
      // Not JSON, treat as comma-separated string
      stocksArray = selectedStocks.split(',').map(s => s.trim()).filter(s => s);
    }
  }
  
  if (stocksArray.length > 0) {
    strategyText += `\nSelected Stocks: ${stocksArray.join(", ")}`;
  }
  
  // Fallback if parsing succeeded but no content
  if (!strategyText) {
    strategyText = "Strategy report generated. No specific recommendations at this time.";
  }
  
  return strategyText;
};
