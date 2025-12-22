from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from database import Base


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    crypto_symbol = Column(String(10), unique=True, index=True)  # BTC, ETH, etc.
    crypto_name = Column(String(50))
    quantity = Column(Float)
    purchase_price = Column(Float)  # USD per unit
    current_price = Column(Float)
    category = Column(String(20))  # altcoin, stablecoin, etc.
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MarketSentiment(Base):
    __tablename__ = "market_sentiment"

    id = Column(Integer, primary_key=True, index=True)
    crypto_symbol = Column(String(10), index=True)
    sentiment_score = Column(Float)  # -1 to 1
    mention_count = Column(Integer)
    positive_percentage = Column(Float)
    source = Column(String(20))  # twitter, reddit
    date = Column(DateTime, server_default=func.now())


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    crypto_symbol = Column(String(10), index=True)
    transaction_type = Column(String(10))  # BUY or SELL
    amount = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, server_default=func.now())
    notes = Column(Text, nullable=True)
