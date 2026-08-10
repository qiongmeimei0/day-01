import os

from dotenv import load_dotenv


load_dotenv()


def env_bool(name, default=False):
    value = os.getenv(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "on"}


OKX_API_KEY = os.getenv("OKX_API_KEY", "")
OKX_SECRET = os.getenv("OKX_SECRET", "")
OKX_PASSWORD = os.getenv("OKX_PASSWORD", "")
CRYPTOPANIC_KEY = os.getenv("CRYPTOPANIC_KEY", "")

SYMBOL = "BTC/USDT:USDT"
OKX_WS_INST_ID = "BTC-USDT-SWAP"
TIMEFRAME = "1h"
OHLCV_LIMIT = 300

LEVERAGE = 10
STOP_LOSS = 0.02
TAKE_PROFIT = 0.04
RISK_PER_TRADE = 0.01
MAX_POSITION_USDT = 50.0
PAPER_BALANCE = 100.0

# 默认只模拟。只有明确设置 LIVE_TRADING=true 才会真实下单。
LIVE_TRADING = env_bool("LIVE_TRADING", False)
OKX_SANDBOX = env_bool("OKX_SANDBOX", False)
HTTP_PROXY = os.getenv("HTTP_PROXY", "").strip()

# 每产生多少根新的已收盘K线后重新训练。
RETRAIN_EVERY_CANDLES = 100
POLL_SECONDS = 60

