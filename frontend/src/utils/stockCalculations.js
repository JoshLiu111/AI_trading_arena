/**
 * Calculate price change percentage
 * Same logic used in both StockCard and StockDetail
 * Formula: change = (currentPrice - previousClose) / previousClose * 100
 */
export const calculatePriceChange = (currentPrice, previousClose) => {
  // Handle null/undefined/0 values
  if (!currentPrice || currentPrice === 0 || !previousClose || previousClose === 0) {
    return { percent: "0.00", amount: 0, isPositive: true };
  }
  
  // Calculate change: (currentPrice - previousClose) / previousClose * 100
  const amount = currentPrice - previousClose;
  const percent = ((amount / previousClose) * 100).toFixed(2);
  const isPositive = amount >= 0;
  
  return { percent, amount, isPositive };
};
