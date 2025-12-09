/**
 * Stocks API
 */
import { fetchAPI } from "./fetchAPI";

// GET /api/v1/stocks/prices - Get real-time prices for stocks
export async function getStockPrices() {
  const data = await fetchAPI("/stocks/prices");
  const stocks = data.stocks || data;

  // Directly use backend data without additional API calls
  // Backend already provides current_price and previous_close
  return stocks.map((stock) => {
    // Use current_price or price field (backward compatibility)
    const currentPrice =
      stock.current_price !== null && stock.current_price !== undefined
        ? stock.current_price
        : stock.price !== null && stock.price !== undefined
        ? stock.price
        : null;

    // Return all fields including company info
    return {
      ticker: stock.ticker,
      name: stock.name || stock.ticker,
      current_price: currentPrice,
      previous_close: stock.previous_close || null,
      open: stock.open,
      high: stock.high,
      low: stock.low,
      volume: stock.volume,
      updated_at: stock.updated_at,
      // Company info fields
      ...(stock.description && { description: stock.description }),
      ...(stock.sector && { sector: stock.sector }),
      ...(stock.industry && { industry: stock.industry }),
      ...(stock.homepage_url && { homepage_url: stock.homepage_url }),
      ...(stock.website && { website: stock.website }),
    };
  });
}

// GET /api/v1/stocks/{ticker}/history - Get historical K-line data
export async function getStockHistory(ticker, params = {}) {
  const queryString = new URLSearchParams(params).toString();
  const endpoint = `/stocks/${ticker}/history${
    queryString ? `?${queryString}` : ""
  }`;
  const historyData = await fetchAPI(endpoint);

  return {
    ticker: historyData.ticker || ticker,
    data: historyData.data || [],
  };
}

