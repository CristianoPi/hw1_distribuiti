import yfinance as yf

def fetch_stock_price(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(period="1d")['Close'].iloc[-1]

print("il valore tornato è: ")
print(fetch_stock_price("AAPL"))