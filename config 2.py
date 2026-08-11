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
HISTORICAL_CANDLES = 5000

LEVERAGE = 10
STOP_LOSS = 0.02
TAKE_PROFIT = 0.04
RISK_PER_TRADE = 0.01
MAX_POSITION_USDT = 50.0
PAPER_BALANCE = 100.0

# 模型和回测参数。
TIME_SERIES_SPLITS = 5
CONFIDENCE_THRESHOLD = 0.60
ROUND_TRIP_FEE_RATE = 0.0010
SLIPPAGE_RATE = 0.0002
# 下一根K线变动不足手续费与噪声阈值时，标签为观望。
MIN_MOVE_THRESHOLD = ROUND_TRIP_FEE_RATE + 2 * SLIPPAGE_RATE

# 默认只模拟。只有明确设置 LIVE_TRADING=true 才会真实下单。
LIVE_TRADING = env_bool("LIVE_TRADING", False)
OKX_SANDBOX = env_bool("OKX_SANDBOX", False)
HTTP_PROXY = os.getenv("HTTP_PROXY", "").strip()

# Gmail邮件通知。密码必须使用Google应用专用密码，不是登录密码。
EMAIL_ENABLED = env_bool("EMAIL_ENABLED", False)
EMAIL_FROM = os.getenv("EMAIL_FROM", "").strip()
EMAIL_TO = os.getenv("EMAIL_TO", "").strip()
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "").replace(" ", "")
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com").strip()
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "465"))

# 每产生多少根新的已收盘K线后重新训练。
RETRAIN_EVERY_CANDLES = 100
POLL_SECONDS = 60
