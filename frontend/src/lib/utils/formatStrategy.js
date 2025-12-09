/**
 * Format strategy content from backend to readable text
 * Supports multiple formats:
 * - Latest format: { summary, trading_strategies: [{ticker, buy_metrics, sell_metrics, quantity, rationale}], selected_stocks }
 * - New format: { summary, stock_preferences: [{ticker, rationale, preferred_quantity}], selected_stocks }
 * - New format: { summary, trading_rules: [{ticker, buy_price, sell_price, quantity, rationale}], selected_stocks }
 * - Old format: { summary, actions: [{ticker, action, quantity, rationale}], selected_stocks }
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
  
  // 1. Add summary
  if (parsed.summary) {
    strategyText = `📊 Strategy Summary\n${"=".repeat(50)}\n${parsed.summary}\n`;
  }
  
  // 2. Add selected stocks
  let stocksArray = [];
  if (Array.isArray(selectedStocks)) {
    stocksArray = selectedStocks;
  } else if (typeof selectedStocks === 'string') {
    try {
      const parsedStocks = JSON.parse(selectedStocks);
      stocksArray = Array.isArray(parsedStocks) ? parsedStocks : [];
    } catch {
      stocksArray = selectedStocks.split(',').map(s => s.trim()).filter(s => s);
    }
  }
  
  // Also check parsed.selected_stocks
  if (stocksArray.length === 0 && parsed.selected_stocks) {
    if (Array.isArray(parsed.selected_stocks)) {
      stocksArray = parsed.selected_stocks;
    } else if (typeof parsed.selected_stocks === 'string') {
      try {
        stocksArray = JSON.parse(parsed.selected_stocks);
      } catch {
        stocksArray = parsed.selected_stocks.split(',').map(s => s.trim()).filter(s => s);
      }
    }
  }
  
  if (stocksArray.length > 0) {
    strategyText += `\n📈 Selected Stocks\n${"=".repeat(50)}\n`;
    strategyText += `${stocksArray.join(", ")}\n`;
  }
  
  // 3. Add trading rules (new format with buy_price/sell_price)
  if (parsed.trading_rules && Array.isArray(parsed.trading_rules) && parsed.trading_rules.length > 0) {
    strategyText += `\n💰 Trading Rules\n${"=".repeat(50)}\n`;
    parsed.trading_rules.forEach((rule, index) => {
      strategyText += `\n${index + 1}. ${rule.ticker}\n`;
      strategyText += `   Buy Price:  $${rule.buy_price?.toFixed(2) || 'N/A'}\n`;
      strategyText += `   Sell Price: $${rule.sell_price?.toFixed(2) || 'N/A'}\n`;
      strategyText += `   Quantity:   ${rule.quantity || 'N/A'} shares\n`;
      if (rule.rationale) {
        // Format rationale with proper line breaks
        const rationaleLines = rule.rationale.split('\n').filter(line => line.trim());
        strategyText += `   Rationale:\n`;
        rationaleLines.forEach(line => {
          strategyText += `   ${line.trim()}\n`;
        });
      }
      // Add separator between rules (except for the last one)
      if (index < parsed.trading_rules.length - 1) {
        strategyText += `\n${"-".repeat(50)}\n`;
      }
    });
  }
  
  // 3.5. Add trading strategies (latest format with buy_metrics/sell_metrics)
  if (parsed.trading_strategies && Array.isArray(parsed.trading_strategies) && parsed.trading_strategies.length > 0) {
    strategyText += `\n📊 Trading Strategies\n${"=".repeat(50)}\n`;
    parsed.trading_strategies.forEach((strat, index) => {
      strategyText += `\n${index + 1}. ${strat.ticker}\n`;
      
      if (strat.rationale) {
        const rationaleLines = strat.rationale.split('\n').filter(line => line.trim());
        strategyText += `   Rationale:\n`;
        rationaleLines.forEach(line => {
          strategyText += `   ${line.trim()}\n`;
        });
      }
      
      if (strat.quantity) {
        strategyText += `   Quantity: ${strat.quantity} shares\n`;
      }
      
      // Add buy conditions
      if (strat.buy_metrics) {
        strategyText += `\n   Buy Conditions:\n`;
        if (strat.buy_metrics.description) {
          strategyText += `   - Description: ${strat.buy_metrics.description}\n`;
        }
        if (strat.buy_metrics.condition) {
          strategyText += `   - Condition: ${strat.buy_metrics.condition}\n`;
        }
      }
      
      // Add sell conditions
      if (strat.sell_metrics) {
        strategyText += `\n   Sell Conditions:\n`;
        if (strat.sell_metrics.description) {
          strategyText += `   - Description: ${strat.sell_metrics.description}\n`;
        }
        if (strat.sell_metrics.condition) {
          strategyText += `   - Condition: ${strat.sell_metrics.condition}\n`;
        }
      }
      
      // Add separator between strategies (except for the last one)
      if (index < parsed.trading_strategies.length - 1) {
        strategyText += `\n${"-".repeat(50)}\n`;
      }
    });
  }
  
  // 3.6. Add stock preferences (simplified format without price points)
  if (parsed.stock_preferences && Array.isArray(parsed.stock_preferences) && parsed.stock_preferences.length > 0) {
    strategyText += `\n📊 Stock Preferences\n${"=".repeat(50)}\n`;
    parsed.stock_preferences.forEach((pref, index) => {
      strategyText += `\n${index + 1}. ${pref.ticker}\n`;
      if (pref.rationale) {
        const rationaleLines = pref.rationale.split('\n').filter(line => line.trim());
        strategyText += `   Rationale:\n`;
        rationaleLines.forEach(line => {
          strategyText += `   ${line.trim()}\n`;
        });
      }
      if (pref.preferred_quantity) {
        strategyText += `   Preferred Quantity: ${pref.preferred_quantity} shares\n`;
      }
      // Add separator between preferences (except for the last one)
      if (index < parsed.stock_preferences.length - 1) {
        strategyText += `\n${"-".repeat(50)}\n`;
      }
    });
  }
  
  // 4. Add actions (old format) for backward compatibility
  if (parsed.actions && Array.isArray(parsed.actions) && parsed.actions.length > 0) {
    if (!strategyText) {
      strategyText = "Trading strategy generated based on current market conditions.\n";
    }
    strategyText += `\n📋 Recommended Actions\n${"=".repeat(50)}\n`;
    parsed.actions.forEach((action, index) => {
      strategyText += `${index + 1}. ${action.action} ${action.quantity} shares of ${action.ticker}\n`;
      if (action.rationale) {
        strategyText += `   Reason: ${action.rationale}\n`;
      }
    });
  }
  
  // Fallback if parsing succeeded but no content
  if (!strategyText) {
    strategyText = "Strategy report generated. No specific recommendations at this time.";
  }
  
  return strategyText;
};
