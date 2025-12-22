import requests


API_URL = "http://localhost:8000/api"


SAMPLE_PORTFOLIOS = [
    {"crypto_symbol": "BTC", "crypto_name": "Bitcoin", "quantity": 0.5, "purchase_price": 45000, "current_price": 52000, "category": "major"},
    {"crypto_symbol": "ETH", "crypto_name": "Ethereum", "quantity": 3, "purchase_price": 2500, "current_price": 3100, "category": "major"},
    {"crypto_symbol": "ADA", "crypto_name": "Cardano", "quantity": 1000, "purchase_price": 0.8, "current_price": 1.2, "category": "altcoin"},
    {"crypto_symbol": "SOL", "crypto_name": "Solana", "quantity": 50, "purchase_price": 80, "current_price": 120, "category": "altcoin"},
    {"crypto_symbol": "DOT", "crypto_name": "Polkadot", "quantity": 100, "purchase_price": 25, "current_price": 35, "category": "altcoin"},
    {"crypto_symbol": "LINK", "crypto_name": "Chainlink", "quantity": 50, "purchase_price": 20, "current_price": 28, "category": "utility"},
    {"crypto_symbol": "USDC", "crypto_name": "USD Coin", "quantity": 5000, "purchase_price": 1, "current_price": 1, "category": "stablecoin"},
    {"crypto_symbol": "XRP", "crypto_name": "Ripple", "quantity": 2000, "purchase_price": 0.5, "current_price": 0.75, "category": "altcoin"},
    {"crypto_symbol": "MATIC", "crypto_name": "Polygon", "quantity": 500, "purchase_price": 1.2, "current_price": 1.8, "category": "altcoin"},
    {"crypto_symbol": "AVAX", "crypto_name": "Avalanche", "quantity": 20, "purchase_price": 100, "current_price": 155, "category": "altcoin"},
]


SAMPLE_SENTIMENTS = [
    {"crypto_symbol": "BTC", "sentiment_score": 0.75, "mention_count": 15000, "positive_percentage": 78, "source": "twitter"},
    {"crypto_symbol": "ETH", "sentiment_score": 0.68, "mention_count": 12000, "positive_percentage": 72, "source": "twitter"},
    {"crypto_symbol": "ADA", "sentiment_score": 0.45, "mention_count": 8000, "positive_percentage": 60, "source": "reddit"},
    {"crypto_symbol": "SOL", "sentiment_score": 0.55, "mention_count": 10000, "positive_percentage": 65, "source": "twitter"},
    {"crypto_symbol": "DOT", "sentiment_score": 0.40, "mention_count": 6000, "positive_percentage": 55, "source": "reddit"},
    {"crypto_symbol": "LINK", "sentiment_score": 0.60, "mention_count": 7000, "positive_percentage": 68, "source": "twitter"},
]


def load_sample_data():
    print("Loading sample portfolio data...")
    for portfolio in SAMPLE_PORTFOLIOS:
        try:
            requests.post(f"{API_URL}/portfolio", json=portfolio)
            print(f" Added {portfolio['crypto_name']}")
        except Exception as e:
            print(f" Error adding {portfolio['crypto_name']}: {e}")

    print("\nLoading sample sentiment data...")
    for sentiment in SAMPLE_SENTIMENTS:
        try:
            requests.post(f"{API_URL}/sentiment", json=sentiment)
            print(f" Added sentiment for {sentiment['crypto_symbol']}")
        except Exception as e:
            print(f" Error adding sentiment: {e}")


if __name__ == "__main__":
    load_sample_data()
