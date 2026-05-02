import pandas as pd
from unittest.mock import patch, MagicMock
from app.data.fetcher import fetch_stock_data

@patch("app.data.fetcher.Ticker")
def test_fetch_stock_data(mock_ticker_class):
    # --- arrange ---
    mock_ticker = MagicMock()
    mock_ticker_class.return_value = mock_ticker

    mock_ticker.info = {
        "trailingPE": 20,
        "trailingEps": 3,
        "revenueGrowth": 0.2,
        "profitMargins": 0.35,
        "grossMargins": 0.55,
        "marketCap": 1000000000
    }

    mock_ticker.history.return_value = pd.DataFrame({
        "Close": [100, 101, 102]
    })

    # --- act ---
    data = fetch_stock_data("AMD")

    # --- assert ---
    assert data["ticker"] == "AMD"
    assert data["pe"] == 20
    assert data["eps"] == 3
    assert data["revenue_growth"] == 0.2
    assert data["profit_margin"] == 0.35
    assert data["gross_margin"] == 0.55
    assert data["market_cap"] == 1000000000

    assert len(data["price_history"]) == 3
    assert list(data["price_history"]) == [100, 101, 102]
