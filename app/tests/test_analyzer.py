from app.logic.analyzer import StockAnalyzer


def test_analyzer_buy():
    analyzer = StockAnalyzer()

    data = {
        "pe": 20,
        "revenue_growth": 0.2,
        "profit_margin": 0.3
    }

    result = analyzer.analyze(data)

    assert result["decision"] == "BUY"
    assert result["score"] == 3

def test_analyzer_sell():
    analyzer = StockAnalyzer()

    data = {
        "pe": 40,
        "revenue_growth": 0.01,
        "profit_margin": 0.05
    }

    result = analyzer.analyze(data)

    assert result["decision"] == "SELL"