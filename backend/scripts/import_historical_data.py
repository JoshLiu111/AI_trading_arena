#!/usr/bin/env python3
"""
Import Historical Stock Data from Local Files
Supports CSV and JSON formats

Usage:
    python scripts/import_historical_data.py --file data/stocks.csv
    python scripts/import_historical_data.py --file data/stocks.json --format json
    python scripts/import_historical_data.py --dir data/stock_data/
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import date, datetime
from typing import List, Dict
import csv
import json

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from models.database import SessionLocal, init_db
from models.crud.stock_price_crud import create_price_data
from models.crud.stock_crud import get_stock, create_stock
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)


def parse_csv_file(file_path: Path) -> Dict[str, List[Dict]]:
    """
    Parse CSV file with stock historical data
    Expected CSV format:
    ticker,date,open,high,low,close,volume,adj_close
    AAPL,2024-01-01,150.0,155.0,149.0,152.0,1000000,152.0
    """
    result = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row.get('ticker', '').strip().upper()
            if not ticker:
                continue
            
            try:
                date_str = row.get('date', '').strip()
                if not date_str:
                    continue
                
                # Parse date (support multiple formats)
                try:
                    price_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        price_date = datetime.strptime(date_str, '%Y/%m/%d').date()
                    except ValueError:
                        logger.warning(f"Invalid date format: {date_str}, skipping")
                        continue
                
                # Parse price data
                price_data = {
                    'date': price_date,
                    'open': float(row.get('open', 0)) if row.get('open') else None,
                    'high': float(row.get('high', 0)) if row.get('high') else None,
                    'low': float(row.get('low', 0)) if row.get('low') else None,
                    'close': float(row.get('close', 0)) if row.get('close') else None,
                    'volume': int(row.get('volume', 0)) if row.get('volume') else None,
                    'adj_close': float(row.get('adj_close', 0)) if row.get('adj_close') else None,
                }
                
                if ticker not in result:
                    result[ticker] = []
                result[ticker].append(price_data)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing row: {row}, error: {e}")
                continue
    
    return result


def parse_json_file(file_path: Path) -> Dict[str, List[Dict]]:
    """
    Parse JSON file with stock historical data
    Expected JSON format:
    {
        "AAPL": [
            {"date": "2024-01-01", "open": 150.0, "high": 155.0, "low": 149.0, "close": 152.0, "volume": 1000000, "adj_close": 152.0},
            ...
        ],
        "MSFT": [...]
    }
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = {}
    for ticker, price_list in data.items():
        ticker = ticker.upper().strip()
        result[ticker] = []
        
        for price_item in price_list:
            try:
                date_str = price_item.get('date', '')
                if isinstance(date_str, str):
                    try:
                        price_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            price_date = datetime.strptime(date_str, '%Y/%m/%d').date()
                        except ValueError:
                            logger.warning(f"Invalid date format: {date_str}, skipping")
                            continue
                else:
                    continue
                
                price_data = {
                    'date': price_date,
                    'open': float(price_item.get('open', 0)) if price_item.get('open') else None,
                    'high': float(price_item.get('high', 0)) if price_item.get('high') else None,
                    'low': float(price_item.get('low', 0)) if price_item.get('low') else None,
                    'close': float(price_item.get('close', 0)) if price_item.get('close') else None,
                    'volume': int(price_item.get('volume', 0)) if price_item.get('volume') else None,
                    'adj_close': float(price_item.get('adj_close', 0)) if price_item.get('adj_close') else None,
                }
                result[ticker].append(price_data)
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing price data for {ticker}: {e}")
                continue
    
    return result


def import_data_to_db(db: Session, data: Dict[str, List[Dict]], tickers: List[str] = None):
    """
    Import parsed data into database
    """
    if tickers is None:
        tickers = list(data.keys())
    
    imported_count = 0
    skipped_count = 0
    
    for ticker in tickers:
        if ticker not in data:
            logger.warning(f"No data found for {ticker}")
            continue
        
        # Ensure stock exists
        if not get_stock(db, ticker):
            logger.info(f"Creating stock record for {ticker}")
            create_stock(
                db,
                ticker=ticker,
                name=ticker,  # Default name, can be updated later
                sector="",
                description="",
                homepage_url="",
                sic_description=""
            )
        
        # Import price data
        price_list = data[ticker]
        for price_data in price_list:
            try:
                create_price_data(
                    db,
                    ticker=ticker,
                    date=price_data['date'],
                    open=price_data.get('open'),
                    high=price_data.get('high'),
                    low=price_data.get('low'),
                    close=price_data.get('close'),
                    volume=price_data.get('volume'),
                    adj_close=price_data.get('adj_close')
                )
                imported_count += 1
            except Exception as e:
                logger.warning(f"Error importing {ticker} on {price_data['date']}: {e}")
                skipped_count += 1
                continue
    
    logger.info(f"Import complete: {imported_count} records imported, {skipped_count} skipped")
    return imported_count, skipped_count


def main():
    parser = argparse.ArgumentParser(description='Import historical stock data from local files')
    parser.add_argument('--file', type=str, help='Path to data file (CSV or JSON)')
    parser.add_argument('--dir', type=str, help='Directory containing data files')
    parser.add_argument('--format', type=str, choices=['csv', 'json', 'auto'], default='auto',
                       help='File format (auto-detect if not specified)')
    parser.add_argument('--tickers', type=str, nargs='+', help='Specific tickers to import (default: all)')
    
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        data = {}
        
        if args.file:
            # Single file
            file_path = Path(args.file)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return
            
            # Auto-detect format
            if args.format == 'auto':
                if file_path.suffix.lower() == '.csv':
                    format_type = 'csv'
                elif file_path.suffix.lower() == '.json':
                    format_type = 'json'
                else:
                    logger.error(f"Unknown file format: {file_path.suffix}")
                    return
            else:
                format_type = args.format
            
            logger.info(f"Parsing {format_type} file: {file_path}")
            if format_type == 'csv':
                data = parse_csv_file(file_path)
            else:
                data = parse_json_file(file_path)
        
        elif args.dir:
            # Directory of files
            dir_path = Path(args.dir)
            if not dir_path.exists():
                logger.error(f"Directory not found: {dir_path}")
                return
            
            # Find all CSV and JSON files
            for file_path in dir_path.glob('*.csv'):
                logger.info(f"Parsing CSV file: {file_path}")
                file_data = parse_csv_file(file_path)
                for ticker, prices in file_data.items():
                    if ticker not in data:
                        data[ticker] = []
                    data[ticker].extend(prices)
            
            for file_path in dir_path.glob('*.json'):
                logger.info(f"Parsing JSON file: {file_path}")
                file_data = parse_json_file(file_path)
                for ticker, prices in file_data.items():
                    if ticker not in data:
                        data[ticker] = []
                    data[ticker].extend(prices)
        
        else:
            parser.print_help()
            return
        
        if not data:
            logger.error("No data found to import")
            return
        
        # Filter by tickers if specified
        tickers = args.tickers
        if tickers:
            tickers = [t.upper().strip() for t in tickers]
            data = {t: data[t] for t in tickers if t in data}
        
        # Import to database
        logger.info(f"Importing data for {len(data)} tickers...")
        imported, skipped = import_data_to_db(db, data, tickers)
        
        db.commit()
        logger.info(f"✅ Successfully imported {imported} price records")
        if skipped > 0:
            logger.warning(f"⚠️  Skipped {skipped} records due to errors")
    
    except Exception as e:
        logger.exception(f"Error during import: {e}")
        db.rollback()
        return 1
    
    finally:
        db.close()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

