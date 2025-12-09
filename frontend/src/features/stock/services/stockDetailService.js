/**
 * Stock Detail Service
 * Business logic for fetching and processing stock detail data
 */

import { 
  getStockPrices, 
  getStockHistory, 
  getAllAccounts, 
  getAccountPositions 
} from "@/lib/api";

/**
 * Convert positions array/object to a map for easy lookup
 */
export function normalizePositions(positionsData) {
  const positionsMap = {};
  
  if (!positionsData?.positions) return positionsMap;
  
  const positions = positionsData.positions;
  
  if (Array.isArray(positions)) {
    positions.forEach((pos) => {
      positionsMap[pos.ticker] = pos;
    });
  } else if (typeof positions === "object") {
    Object.keys(positions).forEach((ticker) => {
      positionsMap[ticker] = positions[ticker];
    });
  }
  
  return positionsMap;
}

/**
 * Enhance stock data with fallback prices from history
 */
export function enhanceStockWithHistory(stock, historyData) {
  const enhanced = { ...stock };
  
  // Fallback for current_price
  if (!enhanced.current_price && historyData?.data?.length > 0) {
    enhanced.current_price = historyData.data[historyData.data.length - 1]?.close || null;
  }
  
  // Set previous_close from history
  if (historyData?.data?.length >= 2) {
    enhanced.previous_close = historyData.data[historyData.data.length - 2]?.close || null;
  } else if (historyData?.data?.length === 1) {
    enhanced.previous_close = historyData.data[0]?.close || null;
  }
  
  return enhanced;
}

/**
 * Fetch stock detail data
 */
export async function fetchStockDetailData(ticker) {
  try {
    // Fetch all data in parallel
    const [stocks, historyData, accountsData] = await Promise.all([
      getStockPrices(),
      getStockHistory(ticker, { days: 7 }),
      getAllAccounts(),
    ]);

    const currentStock = stocks.find((s) => s.ticker === ticker);

    if (!currentStock) {
      throw new Error(`Stock ${ticker} not found`);
    }

    // Enhance stock with history data
    const enhancedStock = enhanceStockWithHistory(currentStock, historyData);

    // Get human account and positions
    const humanAccount = accountsData.find((acc) => acc.account_type === "human");
    
    let humanAccountId = null;
    let accountBalance = 0;
    let accountPositions = {};

    if (humanAccount) {
      humanAccountId = humanAccount.id;
      accountBalance = humanAccount.balance || 0;

      try {
        const positionsData = await getAccountPositions(humanAccount.id);
        accountBalance = positionsData.balance || humanAccount.balance || 0;
        accountPositions = normalizePositions(positionsData);
      } catch (err) {
        console.warn("Failed to fetch account positions:", err);
      }
    }

    return {
      stock: enhancedStock,
      history: historyData,
      accounts: accountsData,
      humanAccountId,
      accountBalance,
      accountPositions,
    };
  } catch (err) {
    throw new Error(err.message || "Failed to load stock data");
  }
}

