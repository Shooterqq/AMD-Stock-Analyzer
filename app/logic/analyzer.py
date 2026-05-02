class StockAnalyzer:
    def __init__(self):
        # wagi (ważność wskaźników)
        self.weights = {
            "pe": 2,
            "forward_pe": 2,
            "revenue_growth": 3,
            "profit_margin": 3,
            "gross_margin": 2,
            "eps": 2,
        }

    def analyze(self, data: dict) -> dict:
        score = 0
        max_score = sum(self.weights.values())

        # PE (niższy = lepiej)
        pe = data.get("pe")
        if pe is not None:
            score += self.weights["pe"] if pe < 25 else 0

        # forward PE
        fpe = data.get("forward_pe")
        if fpe is not None:
            score += self.weights["forward_pe"] if fpe < 22 else 0

        # growth (najważniejsze)
        growth = data.get("revenue_growth")
        if growth is not None:
            score += self.weights["revenue_growth"] if growth > 0.1 else 0

        # profit margin
        pm = data.get("profit_margin")
        if pm is not None:
            score += self.weights["profit_margin"] if pm > 0.2 else 0

        # gross margin
        gm = data.get("gross_margin")
        if gm is not None:
            score += self.weights["gross_margin"] if gm > 0.3 else 0

        # EPS
        eps = data.get("eps")
        if eps is not None:
            score += self.weights["eps"] if eps > 1 else 0

        # normalizacja do 0–100
        normalized = (score / max_score) * 100

        # decyzja
        if normalized >= 70:
            decision = "BUY"
        elif normalized >= 40:
            decision = "HOLD"
        else:
            decision = "SELL"

        return {
            "decision": decision,
            "score": round(normalized, 2)
        }