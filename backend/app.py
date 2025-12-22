from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
from sqlalchemy.orm import Session
from models import Portfolio as PortfolioModel, Base
from schemas import (
    PortfolioCreate, PortfolioUpdate, Portfolio as PortfolioSchema,
    TransactionCreate,
    MarketSentimentBase,
)
from database import engine, get_db
from crud import (
    get_portfolio, get_portfolio_by_symbol, create_portfolio,
    update_portfolio, delete_portfolio, get_sentiments,
    create_sentiment, create_transaction, get_transactions
)

from crud import get_portfolio_by_id, update_portfolio_by_id, delete_portfolio_by_id

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Crypto Portfolio API",
    description="Real-time cryptocurrency portfolio tracking API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== PORTFOLIO ENDPOINTS ==========

@app.get("/api/portfolio", response_model=list[PortfolioSchema])
def read_portfolio(db: Session = Depends(get_db)):
    """Get all portfolio holdings"""
    return get_portfolio(db)

@app.get("/api/portfolio/{symbol_or_id}", response_model=PortfolioSchema)
def read_portfolio_by_symbol_or_id(symbol_or_id: str, db: Session = Depends(get_db)):
    """Get specific portfolio holding by symbol (e.g. BTC) or numeric id (e.g. 11)."""
    db_portfolio = None
    try:
        portfolio_id = int(symbol_or_id)
        db_portfolio = get_portfolio_by_id(db, portfolio_id)
    except ValueError:
        db_portfolio = get_portfolio_by_symbol(db, symbol_or_id.upper())
    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio for {symbol_or_id} not found"
        )
    return db_portfolio

@app.post("/api/portfolio", response_model=PortfolioSchema, status_code=status.HTTP_201_CREATED)
def create_new_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    """Create new portfolio holding"""
    existing = get_portfolio_by_symbol(db, portfolio.crypto_symbol.upper())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Portfolio for {portfolio.crypto_symbol} already exists"
        )
    return create_portfolio(db, portfolio)

@app.put("/api/portfolio/{symbol_or_id}", response_model=PortfolioSchema)
def update_portfolio_holding(symbol_or_id: str, portfolio: PortfolioUpdate, db: Session = Depends(get_db)):
    """Update portfolio holding by symbol (e.g. BTC) or numeric id (e.g. 11)."""
    updated = None
    try:
        portfolio_id = int(symbol_or_id)
        updated = update_portfolio_by_id(db, portfolio_id, portfolio)
    except ValueError:
        updated = update_portfolio(db, symbol_or_id.upper(), portfolio)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio for {symbol_or_id} not found"
        )
    return updated

@app.delete("/api/portfolio/{symbol_or_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_holding(symbol_or_id: str, db: Session = Depends(get_db)):
    """Delete portfolio holding by symbol (e.g. BTC) or numeric id (e.g. 11)."""
    deleted = None
    try:
        portfolio_id = int(symbol_or_id)
        deleted = delete_portfolio_by_id(db, portfolio_id)
    except ValueError:
        deleted = delete_portfolio(db, symbol_or_id.upper())
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio for {symbol_or_id} not found"
        )

# ========== SENTIMENT ENDPOINTS ==========

@app.get("/api/sentiment")
def read_sentiments(db: Session = Depends(get_db)):
    """Get market sentiment data"""
    return get_sentiments(db)

@app.post("/api/sentiment", status_code=status.HTTP_201_CREATED)
def add_sentiment(sentiment: MarketSentimentBase, db: Session = Depends(get_db)):
    """Add sentiment data"""
    return create_sentiment(db, sentiment)

# ========== TRANSACTION ENDPOINTS ==========

@app.post("/api/transactions", status_code=status.HTTP_201_CREATED)
def create_new_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Create transaction record"""
    return create_transaction(db, transaction)

@app.get("/api/transactions")
def read_transactions(symbol: str = None, db: Session = Depends(get_db)):
    """Get transactions (optionally filtered by symbol)"""
    return get_transactions(db, symbol)

# ========== HEALTH CHECK ==========

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Crypto Portfolio API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)