import ccxt
from config import *

exchange = ccxt.okx({
    "apiKey": OKX_API_KEY,
    "secret": OKX_SECRET,
    "password": OKX_PASSWORD,
    'enableRateLimit': True,
    'proxies': {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    }
})

def fetch_ohlcv():
    return exchange.fetch_ohlcv(SYMBOL, timeframe="1h", limit=200)

def fetch_position():
    try:
        positions = exchange.fetch_positions()
        for p in positions:
           if p["symbol"] == SYMBOL and float(p["contracts"])>0:
              return True
        return False
    except Exception as e:
        print("position check error:", e)
        return False

def limit_buy(amount, price):
    return exchange.create_limit_buy_order(SYMBOL, amount, price)

def limit_sell(amount, price):
    return exchange.create_limit_sell_order(SYMBOL, amount, price)