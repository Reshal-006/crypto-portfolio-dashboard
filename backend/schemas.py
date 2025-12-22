from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PortfolioCreate(BaseModel):
    crypto_symbol: str
    crypto_name: str
    quantity: float
    purchase_price: float
    current_price: float
    category: str


class PortfolioUpdate(BaseModel):
    quantity: Optional[float] = None
    current_price: Optional[float] = None
    category: Optional[str] = None


class Portfolio(BaseModel):
    id: int
    crypto_symbol: str
    crypto_name: str
    quantity: float
    purchase_price: float
    current_price: float
    category: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MarketSentimentBase(BaseModel):
    crypto_symbol: str
    sentiment_score: float
    mention_count: int
    positive_percentage: float
    source: str


class TransactionCreate(BaseModel):
    crypto_symbol: str
    transaction_type: str
    amount: float
    price: float
    notes: Optional[str] = None
