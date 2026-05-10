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

        return {

            "ticker": ticker,

            "nombre": info.get("longName"),
            "sector": info.get("sector"),
            "industria": info.get("industry"),
            "pais": info.get("country"),

            "precio_actual": info.get("currentPrice"),

            "market_cap": info.get("marketCap"),

            "pe_trailing": info.get("trailingPE"),

            "roe": info.get("returnOnEquity"),

            "profit_margin": info.get("profitMargins"),

            "revenue_growth": info.get("revenueGrowth"),

            "debt_to_equity": info.get("debtToEquity"),

            "fcf": info.get("freeCashflow"),

            "eps": info.get("trailingEps"),

            "book_value": info.get("bookValue"),

            "beta": info.get("beta"),

            "dividend_yield": info.get("dividendYield")
        }

    except Exception as e:

        return {
            "error": True,
            "mensaje": str(e),
            "ticker": ticker
        }
