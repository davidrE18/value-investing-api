from fastapi import FastAPI
import yfinance as yf
import numpy as np

app = FastAPI()

@app.get("/")
def home():

    return {
        "status": "running",
        "message": "Quantamental Investing Engine"
    }

# ==========================================
# DCF ENGINE
# ==========================================

def calcular_dcf(
    fcf,
    growth,
    terminal_growth=0.03,
    discount_rate=0.10,
    years=5
):

    if fcf <= 0:
        return 0

    flujos = []

    current_fcf = fcf

    for year in range(1, years + 1):

        current_fcf *= (1 + growth)

        pv = current_fcf / ((1 + discount_rate) ** year)

        flujos.append(pv)

    terminal_value = (
        current_fcf * (1 + terminal_growth)
    ) / (discount_rate - terminal_growth)

    terminal_pv = terminal_value / (
        (1 + discount_rate) ** years
    )

    total_value = sum(flujos) + terminal_pv

    return total_value

# ==========================================
# MARKET EXPECTATIONS MOCK
# ==========================================

def market_expectations(ticker):

    expectations = {

        "AAPL": {
            "analyst_target": 305,
            "sentiment": "BULLISH",
            "ai_premium": 0.20
        },

        "MSFT": {
            "analyst_target": 520,
            "sentiment": "VERY_BULLISH",
            "ai_premium": 0.25
        },

        "NVDA": {
            "analyst_target": 180,
            "sentiment": "EXTREME_BULLISH",
            "ai_premium": 0.35
        }
    }

    return expectations.get(ticker, {
        "analyst_target": None,
        "sentiment": "NEUTRAL",
        "ai_premium": 0
    })

# ==========================================
# MAIN ENDPOINT
# ==========================================

@app.get("/stock/{ticker}")
def get_stock(ticker: str):

    try:

        stock = yf.Ticker(ticker)

        info = stock.info

        # =====================================
        # VARIABLES BASE
        # =====================================

        precio = info.get("currentPrice", 0) or 0

        eps = info.get("trailingEps", 0) or 0

        book = info.get("bookValue", 0) or 0

        roe = info.get("returnOnEquity", 0) or 0

        growth = info.get("revenueGrowth", 0) or 0

        debt = info.get("debtToEquity", 0) or 0

        fcf = info.get("freeCashflow", 0) or 0

        market_cap = info.get("marketCap", 0) or 0

        sector = info.get("sector", "Unknown")

        # =====================================
        # GROWTH AJUSTADO POR SECTOR
        # =====================================

        sector_growth = {
            "Technology": 0.12,
            "Healthcare": 0.08,
            "Financial Services": 0.05,
            "Consumer Defensive": 0.04,
            "Industrials": 0.06
        }

        adjusted_growth = sector_growth.get(
            sector,
            max(growth, 0.05)
        )

        # =====================================
        # GRAHAM
        # =====================================

        if eps > 0 and book > 0:
            graham = (22.5 * eps * book) ** 0.5
        else:
            graham = 0

        # =====================================
        # PETER LYNCH
        # =====================================

        if eps > 0:
            lynch = eps * min(adjusted_growth * 100, 25)
        else:
            lynch = 0

        # =====================================
        # DCF SCENARIOS
        # =====================================

        dcf_bear = calcular_dcf(
            fcf,
            growth=0.03,
            discount_rate=0.12
        )

        dcf_base = calcular_dcf(
            fcf,
            growth=adjusted_growth,
            discount_rate=0.10
        )

        dcf_bull = calcular_dcf(
            fcf,
            growth=max(adjusted_growth * 1.5, 0.15),
            discount_rate=0.09
        )

        # =====================================
        # DCF PER SHARE
        # =====================================

        shares = 0

        if precio > 0:
            shares = market_cap / precio

        if shares > 0:

            dcf_bear_ps = dcf_bear / shares
            dcf_base_ps = dcf_base / shares
            dcf_bull_ps = dcf_bull / shares

        else:

            dcf_bear_ps = 0
            dcf_base_ps = 0
            dcf_bull_ps = 0

        # =====================================
        # MARKET EXPECTATIONS
        # =====================================

        market = market_expectations(ticker)

        analyst_target = market["analyst_target"]

        sentiment = market["sentiment"]

        ai_premium = market["ai_premium"]

        # =====================================
        # WEIGHTED INTRINSIC VALUE
        # =====================================

        valores = []

        if graham > 0:
            valores.append(graham * 0.15)

        if lynch > 0:
            valores.append(lynch * 0.20)

        if dcf_base_ps > 0:
            valores.append(dcf_base_ps * 0.40)

        if dcf_bull_ps > 0:
            valores.append(dcf_bull_ps * 0.15)

        if analyst_target:
            valores.append(analyst_target * 0.10)

        intrinsic = sum(valores)

        # =====================================
        # AI PREMIUM
        # =====================================

        intrinsic_adjusted = intrinsic * (
            1 + ai_premium
        )

        # =====================================
        # QUALITY SCORE
        # =====================================

        quality = 0

        if roe > 0.15:
            quality += 3

        if debt < 100:
            quality += 2

        if fcf > 0:
            quality += 2

        if adjusted_growth > 0.08:
            quality += 2

        if precio > 10:
            quality += 1

        # =====================================
        # MARGIN SAFETY
        # =====================================

        if intrinsic_adjusted > 0:

            margin_safety = (
                (intrinsic_adjusted - precio)
                / intrinsic_adjusted
            ) * 100

        else:

            margin_safety = 0

        # =====================================
        # SIGNAL ENGINE
        # =====================================

        if margin_safety > 25 and quality >= 8:
            signal = "BUY"

        elif margin_safety > 10:
            signal = "WATCH"

        elif margin_safety < -20:
            signal = "SELL"

        else:
            signal = "HOLD"

        # =====================================
        # RESPONSE
        # =====================================

        return {

            # IDENTIFICACION
            "ticker": ticker,
            "nombre": info.get("longName"),
            "sector": sector,

            # MARKET
            "precio_actual": precio,
            "market_cap": market_cap,

            # FUNDAMENTALS
            "eps": eps,
            "book_value": book,
            "roe": roe,
            "revenue_growth": growth,
            "profit_margin": info.get("profitMargins"),
            "debt_to_equity": debt,
            "fcf": fcf,

            # VALUATIONS
            "graham_value": round(graham, 2),
            "lynch_value": round(lynch, 2),

            # DCF
            "dcf_bear": round(dcf_bear_ps, 2),
            "dcf_base": round(dcf_base_ps, 2),
            "dcf_bull": round(dcf_bull_ps, 2),

            # MARKET EXPECTATIONS
            "analyst_target": analyst_target,
            "market_sentiment": sentiment,
            "ai_premium": ai_premium,

            # FINAL ENGINE
            "intrinsic_value": round(intrinsic_adjusted, 2),

            # SCORES
            "quality_score": quality,

            # SAFETY
            "margin_safety": round(margin_safety, 2),

            # SIGNAL
            "signal": signal
        }

    except Exception as e:

        return {
            "error": True,
            "mensaje": str(e),
            "ticker": ticker
        }
