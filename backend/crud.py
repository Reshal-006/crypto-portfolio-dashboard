from typing import Optional

from sqlalchemy.orm import Session

from models import MarketSentiment, Portfolio, Transaction
from schemas import MarketSentimentBase, PortfolioCreate, PortfolioUpdate, TransactionCreate

# Portfolio CRUD
def get_portfolio(db: Session):
    return db.query(Portfolio).all()

def get_portfolio_by_symbol(db: Session, symbol: str):
    return db.query(Portfolio).filter(Portfolio.crypto_symbol == symbol).first()


def get_portfolio_by_id(db: Session, portfolio_id: int):
    return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

def create_portfolio(db: Session, portfolio: PortfolioCreate):
    db_portfolio = Portfolio(**portfolio.model_dump())
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def update_portfolio(db: Session, symbol: str, portfolio: PortfolioUpdate):
    db_portfolio = get_portfolio_by_symbol(db, symbol)
    if not db_portfolio:
        return None
    
    update_data = portfolio.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_portfolio, field, value)
    
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio


def update_portfolio_by_id(db: Session, portfolio_id: int, portfolio: PortfolioUpdate):
    db_portfolio = get_portfolio_by_id(db, portfolio_id)
    if not db_portfolio:
        return None

    update_data = portfolio.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_portfolio, field, value)

    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def delete_portfolio(db: Session, symbol: str):
    db_portfolio = get_portfolio_by_symbol(db, symbol)
    if db_portfolio:
        db.delete(db_portfolio)
        db.commit()
    return db_portfolio


def delete_portfolio_by_id(db: Session, portfolio_id: int):
    db_portfolio = get_portfolio_by_id(db, portfolio_id)
    if db_portfolio:
        db.delete(db_portfolio)
        db.commit()
    return db_portfolio

# Sentiment CRUD
def get_sentiments(db: Session):
    return db.query(MarketSentiment).all()

def create_sentiment(db: Session, sentiment: MarketSentimentBase):
    db_sentiment = MarketSentiment(**sentiment.model_dump())
    db.add(db_sentiment)
    db.commit()
    db.refresh(db_sentiment)
    return db_sentiment

# Transaction CRUD
def create_transaction(db: Session, transaction: TransactionCreate):
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, symbol: Optional[str] = None):
    query = db.query(Transaction)
    if symbol:
        query = query.filter(Transaction.crypto_symbol == symbol)
    return query.all()