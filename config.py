import os
from dotenv import load_dotenv
load_dotenv()
OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_SECRET = os.getenv("OKX_SECRET")
OKX_PASSWORD = os.getenv("OKX_PASSWORD")
CRYPTOPANIC_KEY = os.getenv("CRYPTOPANIC_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
#交易 BTC 合约。
SYMBOL = "BTC/USDT:USDT"
#10倍杠杆
LEVERAGE = 10
#每次交易：50 USDT
ORDER_SIZE = 50
#止损: 2%
STOP_LOSS = 0.02
#止盈: 4%
TAKE_PROFIT = 0.04
#风险控制参数: 每一笔交易最多只冒账户资金的 1% 风险
RISK_PER_TRADE = 0.01