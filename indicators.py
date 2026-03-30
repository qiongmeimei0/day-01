import pandas as pd

def rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100/(1+rs))
    return df

def macd(df):
    ema12 = df['close'].ewm(span=12).mean()
    ema26 = df['close'].ewm(span=26).mean()
    df['macd'] = ema12 - ema26
    df['signal'] = df['macd'].ewm(span=9).mean()
    return df

def bollinger(df):
    df['ma'] = df['close'].rolling(20).mean()
    df['std'] = df['close'].rolling(20).std()
    df['upper'] = df['ma'] + 2*df['std']
    df['lower'] = df['ma'] - 2*df['std']
    return df