"""
Database initialization script.
Run this script to create all database tables.

Usage:
    python init_db.py
"""
from models.database import init_database, check_connection

if __name__ == "__main__":
    print("Initializing database...")
    
    # Check connection first
    if not check_connection():
        print("❌ Cannot connect to database. Please check your DATABASE_URL in .env")
        exit(1)
    
    # Initialize database (creates all tables)
    init_database()
    print("✅ Database initialization complete!")

