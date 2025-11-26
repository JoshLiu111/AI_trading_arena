"""
FastAPI dependencies for database sessions.
"""
from models.database import SessionLocal

def get_db():
    """
    FastAPI dependency: Provide a DB session per request.
    Automatically closes the session after the request.
    
    Usage in routes:
        @router.get("/items/")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

