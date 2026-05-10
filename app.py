from fastapi import FastAPI
import yfinance as yf

app = FastAPI()

@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Value Investing API"
    }

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

        # =====================================
        # GRAHAM VALUE
        # =====================================

        if eps > 0 and book > 0:
            graham = (22.5 * eps * book) ** 0.5
        else:
            graham = 0

        # =====================================
        # PETER LYNCH VALUE
        # =====================================

        if eps > 0 and growth > 0:
            lynch = eps * min(growth * 100, 25)
        else:
            lynch = 0

        # =====================================
        # QUALITY SCORE
        # =====================================

        quality = 0

        # ROE
        if roe > 0.15:
            quality += 3

        # DEBT
        if debt < 100:
            quality += 2

        # FREE CASH FLOW
        if fcf > 0:
            quality += 2

        # GROWTH
        if growth > 0.05:
            quality += 2

        # PRICE FILTER
        if precio > 10:
            quality += 1

        # =====================================
        # INTRINSIC VALUE
        # =====================================

        valores = []

        if graham > 0:
            valores.append(graham)

        if lynch > 0:
            valores.append(lynch)

        if len(valores) > 0:
            intrinsic = sum(valores) / len(valores)
        else:
            intrinsic = 0

        # =====================================
        # MARGIN OF SAFETY
        # =====================================

        if intrinsic > 0:
            margin_safety = ((intrinsic - precio) / intrinsic) * 100
        else:
            margin_safety = 0

        # =====================================
        # SIGNAL ENGINE
        # =====================================

        if margin_safety > 30 and quality >= 7:
            signal = "BUY"

        elif margin_safety > 15:
            signal = "WATCH"

        elif margin_safety < 0:
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
            "sector": info.get("sector"),
            "industria": info.get("industry"),
            "pais": info.get("country"),

            # MARKET DATA
            "precio_actual": precio,
            "market_cap": info.get("marketCap"),

            # RATIOS
            "pe_trailing": info.get("trailingPE"),
            "roe": roe,
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": growth,
            "debt_to_equity": debt,

            # CASHFLOW
            "fcf": fcf,

            # ACCOUNTING
            "eps": eps,
            "book_value": book,

            # RISK
            "beta": info.get("beta"),

            # DIVIDEND
            "dividend_yield": info.get("dividendYield"),

            # =====================================
            # VALUATION ENGINE
            # =====================================

            "graham_value": round(graham, 2),
            "lynch_value": round(lynch, 2),
            "intrinsic_value": round(intrinsic, 2),

            # =====================================
            # SCORES
            # =====================================

            "quality_score": quality,

            # =====================================
            # SAFETY
            # =====================================

            "margin_safety": round(margin_safety, 2),

            # =====================================
            # SIGNAL
            # =====================================

            "signal": signal
        }

    except Exception as e:

        return {
            "error": True,
            "mensaje": str(e),
            "ticker": ticker
        }
