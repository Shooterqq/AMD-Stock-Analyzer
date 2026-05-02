from app.data.fetcher import fetch_stock_data
from app.logic.analyzer import StockAnalyzer


def get_stock_analysis(ticker: str) -> dict:
    data = fetch_stock_data(ticker)

    analyzer = StockAnalyzer()   # ← obiekt
    analysis = analyzer.analyze(data)

    return {
        "ticker": ticker,
        "analysis": analysis
    }