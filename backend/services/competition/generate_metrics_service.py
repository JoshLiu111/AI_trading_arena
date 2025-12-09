# backend/services/competition/generate_metrics_service.py

"""
Generate Metrics Service - Calculate stock metrics for AI analysis
"""

from typing import List, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session
import statistics

from config import settings
from models.crud.stock_price_crud import get_price_history


class MetricsService:
    def __init__(self):
        self.stock_pool = settings.STOCK_POOL
    
    def calculate_metrics(self, db: Session, days: int = 7) -> List[Dict]:
        """
        Calculate metrics for all stocks in pool
        
        Returns metrics:
        - current_price: Latest close price
        - price_7d_ago: Close price 7 days ago
        - change_7d_percent: 7-day price change %
        - avg_volume_7d: Average volume over 7 days
        - volatility_7d: Price volatility (std dev of daily returns)
        - trend: UP / DOWN / SIDEWAYS
        """
        result = []
        
        for ticker in self.stock_pool:
            history = get_price_history(db, ticker, days=days)
            
            if not history or len(history) < 2:
                continue
            
            # history is ordered desc, so [0] is latest
            prices = [float(h.close) for h in history if h.close]
            volumes = [int(h.volume) for h in history if h.volume]
            
            if len(prices) < 2:
                continue
            
            current_price = prices[0]
            price_7d_ago = prices[-1]
            change_7d = current_price - price_7d_ago
            change_7d_percent = (change_7d / price_7d_ago) * 100 if price_7d_ago else 0
            
            # Calculate daily returns for volatility
            daily_returns = []
            for i in range(len(prices) - 1):
                ret = (prices[i] - prices[i+1]) / prices[i+1] * 100
                daily_returns.append(ret)
            
            volatility = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0
            avg_volume = int(statistics.mean(volumes)) if volumes else 0
            
            # Determine trend
            if change_7d_percent > 2:
                trend = "UP"
            elif change_7d_percent < -2:
                trend = "DOWN"
            else:
                trend = "SIDEWAYS"
            
            result.append({
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "price_7d_ago": round(price_7d_ago, 2),
                "change_7d_percent": round(change_7d_percent, 2),
                "avg_volume_7d": avg_volume,
                "volatility_7d": round(volatility, 2),
                "trend": trend
            })
        
        return result
    
    def format_for_ai(self, metrics: List[Dict]) -> str:
        """Format metrics as a prompt for AI"""
        lines = ["Stock Market Analysis (Last 7 Days):", ""]
        
        for m in metrics:
            lines.append(
                f"- {m['ticker']}: ${m['current_price']} "
                f"({m['change_7d_percent']:+.2f}% 7d) "
                f"Vol: {m['avg_volume_7d']:,} "
                f"Volatility: {m['volatility_7d']:.2f}% "
                f"Trend: {m['trend']}"
            )
        
        return "\n".join(lines)


# Singleton instance
metrics_service = MetricsService()
