# backend/services/competition/historical_data_service.py

"""
Historical Data Service - Format 7-day historical data for AI analysis
"""

from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import date

from config import settings
from models.crud.stock_price_crud import get_price_history


class HistoricalDataService:
    def __init__(self):
        self.stock_pool = settings.STOCK_POOL
    
    def get_all_stocks_history(self, db: Session, days: int = 7) -> Dict[str, List[Dict]]:
        """
        Get 7-day historical data for all stocks in pool
        
        Returns:
        {
            "AAPL": [
                {"date": "2025-12-05", "open": 150.0, "high": 152.0, "low": 149.0, "close": 151.0, "volume": 1000000},
                ...
            ],
            "MSFT": [...],
            ...
        }
        """
        result = {}
        
        for ticker in self.stock_pool:
            history = get_price_history(db, ticker, days=days)
            
            if not history:
                result[ticker] = []
                continue
            
            # Convert to list of dicts, ordered by date (oldest first)
            history_list = []
            for h in reversed(history):  # Reverse to get oldest first
                history_list.append({
                    "date": h.date.isoformat() if h.date else None,
                    "open": float(h.open) if h.open else None,
                    "high": float(h.high) if h.high else None,
                    "low": float(h.low) if h.low else None,
                    "close": float(h.close) if h.close else None,
                    "volume": int(h.volume) if h.volume else None,
                    "adj_close": float(h.adj_close) if h.adj_close else None
                })
            
            result[ticker] = history_list
        
        return result
    
    def format_for_ai(self, history_data: Dict[str, List[Dict]]) -> str:
        """
        Format historical data as JSON string for AI (preferred format for LLM analysis)
        Returns JSON format which is easier for AI to parse and analyze
        """
        import json
        return json.dumps(history_data, indent=2)
    
    def format_as_text_for_ai(self, history_data: Dict[str, List[Dict]]) -> str:
        """
        Format historical data as a detailed text prompt for AI (alternative format)
        Returns a formatted string with all stock data
        """
        lines = ["Stock Historical Data (Last 7 Days):", "=" * 60, ""]
        
        for ticker in sorted(history_data.keys()):
            data = history_data[ticker]
            if not data:
                lines.append(f"{ticker}: No data available")
                lines.append("")
                continue
            
            lines.append(f"{ticker} - {len(data)} days of data:")
            lines.append("-" * 40)
            
            for day in data:
                date_str = day.get("date", "N/A")
                open_price = day.get("open")
                high_price = day.get("high")
                low_price = day.get("low")
                close_price = day.get("close")
                volume = day.get("volume")
                
                price_str = f"O: ${open_price:.2f}" if open_price else "O: N/A"
                price_str += f" H: ${high_price:.2f}" if high_price else " H: N/A"
                price_str += f" L: ${low_price:.2f}" if low_price else " L: N/A"
                price_str += f" C: ${close_price:.2f}" if close_price else " C: N/A"
                volume_str = f"Vol: {volume:,}" if volume else "Vol: N/A"
                
                lines.append(f"  {date_str}: {price_str} | {volume_str}")
            
            lines.append("")
        
        return "\n".join(lines)


# Singleton instance
historical_data_service = HistoricalDataService()

