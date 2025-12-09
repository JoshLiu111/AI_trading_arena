# backend/models/schema/stock.py

"""
Stock SQLAlchemy Model
"""

from sqlalchemy import Column, Integer, String
from models.database import Base


class Stock(Base):
    """Stock model for stock information"""
    
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=True, default="")
    description = Column(String, nullable=True, default="")
    homepage_url = Column(String, nullable=True, default="")
    sic_description = Column(String, nullable=True, default="")
    
    def __repr__(self):
        return f"<Stock(id={self.id}, ticker={self.ticker}, name={self.name})>"
