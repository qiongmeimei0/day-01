from indicators import rsi, macd, bollinger
from sentiment import news_sentiment, fear_greed
from ai_model import predict

def generate_signal(df):
    # RSI/MACD/BOLL
    df = rsi(df)
    df = macd(df)
    df = bollinger(df)

    last = df.iloc[-1]

    signal = 0
    # 布林带信号
    if last['close'] > last['upper']:
        signal -= 1
    elif last['close'] < last['lower']:
        signal += 1

    # AI 信号
#    ai_sig = predict(df)
#    signal += ai_sig

    # 新闻情绪
#    signal += news_sentiment()
#    signal += fear_greed()

    # 最终信号: -1 卖出, 1 买入, 0 中性
    return 1 if signal>0 else -1 if signal<0 else 0