"""
SQLAlchemy models for database tables.

Define your database models here by inheriting from Base:

Example:
    from timber_common.services import Base
    from sqlalchemy import Column, Integer, String, Float, DateTime
    
    class StockPrice(Base):
        __tablename__ = "stock_prices"
        
        id = Column(Integer, primary_key=True, index=True)
        symbol = Column(String, index=True)
        date = Column(DateTime)
        close = Column(Float)
        volume = Column(Integer)
"""

from common.services.db_service import Base

__all__ = ['Base']