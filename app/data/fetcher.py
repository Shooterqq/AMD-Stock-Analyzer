from yfinance import Ticker

def fetch_stock_data(ticker: str = "AMD") -> dict:
    """
    Fetch stock data from Yahoo Finance.

    Returns:
        dict: basic financial metrics + 6-month price history
    """
    stock = Ticker(ticker)

    info = stock.info
    history = stock.history(period="6mo")

    return {
        "ticker": ticker,
        "price_history": history["Close"],
        "pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "eps": info.get("trailingEps"),
        "revenue_growth": info.get("revenueGrowth"),
        "profit_margin": info.get("profitMargins"),
        "gross_margin": info.get("grossMargins"),
        "market_cap": info.get("marketCap"),
    }