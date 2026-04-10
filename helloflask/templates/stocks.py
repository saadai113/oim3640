import yfinance as yf

def get_price(symbol):
    stock = yf.Ticker(symbol)
    price = stock.info['regularMarketPrice']
    return price