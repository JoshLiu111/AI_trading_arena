# backend/init_postgres_db.py

"""
PostgreSQL Database Initialization Script
Creates the stock_arena database and all tables
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
import os
import sys

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Database connection parameters (update these as needed)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
# On macOS, default user is usually the current system user, not "postgres"
DB_USER = os.getenv("DB_USER", os.getenv("USER", "postgres"))
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = "stock_arena"

def create_database():
    """Create the stock_arena database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (default postgres database)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"  # Connect to default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✅ Database '{DB_NAME}' created successfully")
        else:
            print(f"ℹ️  Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        raise

def create_tables():
    """Create all tables using SQLAlchemy"""
    # Update DATABASE_URL to use the new database
    database_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Create engine
    engine = create_engine(database_url)
    
    # Import all models to register them
    from models.schema import Account, Stock, StockPrice, TradingStrategy, Transaction
    from models.database import Base
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")
    
    # Verify tables were created
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        tables = [row[0] for row in result]
        print(f"\n📊 Created tables: {', '.join(tables)}")

if __name__ == "__main__":
    print("🚀 Initializing PostgreSQL database 'stock_arena'...\n")
    
    # Step 1: Create database
    create_database()
    
    # Step 2: Create tables
    create_tables()
    
    print("\n✅ Database initialization complete!")
    print(f"\n📝 Update your .env file with:")
    print(f"   DATABASE_URL=postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

