"""
Database connection and session management.
Provides SQLAlchemy engine, session factory, and utility functions.
"""
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings

# ---------------------------------------------------------
# 1. Create SQLAlchemy Engine
# ---------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ---------------------------------------------------------
# 2. Create Session Factory (for ORM operations)
# ---------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ---------------------------------------------------------
# 3. Base class for all models
# ---------------------------------------------------------
Base = declarative_base()

# ---------------------------------------------------------
# 4. Initialize database (create all tables)
# ---------------------------------------------------------
def init_database():
    """
    Initialize database by creating all tables.
    WARNING: This will drop existing tables!
    """
    from models import account_models, stock_models

    print("🧹 Dropping & Recreating all tables...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("✅ Database initialized.")

# ---------------------------------------------------------
# 5. Context Manager for Session (for non-FastAPI scenarios)
# ---------------------------------------------------------
@contextmanager
def get_session():
    """
    Context manager for database sessions.
    Use this in scripts and services (not in FastAPI routes).
    For FastAPI routes, use get_db() from models.deps instead.
    
    Example:
        with get_session() as session:
            account = session.query(Account).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ---------------------------------------------------------
# 6. Test database connection
# ---------------------------------------------------------
def check_connection() -> bool:
    """
    Test database connection.
    Returns True if connection is successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("🔌 Database connection OK.")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

