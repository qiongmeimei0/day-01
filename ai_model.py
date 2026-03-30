import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import talib  # 需要安装：pip install TA-Lib

# 全局模型
model = RandomForestClassifier()

# ---- 添加技术指标函数 ----
def add_indicators(df):
    """为K线数据增加RSI和MACD列"""
    df = df.copy()
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    # volume已经存在
    df.dropna(inplace=True)  # 去掉计算指标后可能产生的NaN
    return df

# ---- 训练模型 ----
def train(df):
    df = add_indicators(df)
    features = df[['rsi','macd','volume']]
    target = (df['close'].shift(-1) > df['close']).astype(int)
    model.fit(features[:-1], target[:-1])
    print("AI模型训练完成")

# ---- 预测信号 ----
def predict(df):
    df = add_indicators(df)
    latest = df[['rsi','macd','volume']].iloc[-1:]
    pred = model.predict(latest)[0]
    return 1 if pred == 1 else -1  # 1=买入, -1=卖出

# ---- 保存模型 ----
def save_model():
    joblib.dump(model, "rf_model.pkl")
    print("AI模型已保存到 rf_model.pkl")

# ---- 加载模型 ----
def load_model():
    global model
    try:
        model = joblib.load("rf_model.pkl")
        print("AI模型加载成功")
    except FileNotFoundError:
        print("未找到模型文件 rf_model.pkl，请先训练")
        raise