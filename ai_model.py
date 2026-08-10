from pathlib import Path

import joblib
import talib
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.validation import check_is_fitted


FEATURES = ["rsi", "macd", "macd_hist", "volume"]
MODEL_PATH = Path(__file__).with_name("rf_model.pkl")
MIN_TRAIN_ROWS = 60

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)


def add_indicators(df):
    """返回增加 RSI、MACD 的K线副本。"""
    required = {"close", "volume"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"K线缺少字段: {sorted(missing)}")

    result = df.copy()
    result["rsi"] = talib.RSI(result["close"], timeperiod=14)
    result["macd"], result["macd_signal"], result["macd_hist"] = talib.MACD(
        result["close"], fastperiod=12, slowperiod=26, signalperiod=9
    )
    return result.dropna().reset_index(drop=True)


def train(df):
    """用已收盘K线训练，并返回训练准确率（仅用于运行检查）。"""
    prepared = add_indicators(df)
    if len(prepared) < MIN_TRAIN_ROWS:
        raise ValueError(f"有效K线不足，需要至少 {MIN_TRAIN_ROWS} 根")

    features = prepared[FEATURES].iloc[:-1]
    target = (prepared["close"].shift(-1) > prepared["close"]).astype(int).iloc[:-1]
    if target.nunique() < 2:
        raise ValueError("训练数据只有一种涨跌结果，无法训练分类模型")

    model.fit(features, target)
    score = model.score(features, target)
    print(f"AI模型训练完成，样本内准确率: {score:.2%}")
    return score


def predict(df):
    """返回 1（看涨）或 -1（看跌）。"""
    check_is_fitted(model)
    prepared = add_indicators(df)
    if prepared.empty:
        raise ValueError("指标计算后没有可用于预测的K线")
    prediction = model.predict(prepared[FEATURES].iloc[-1:])[0]
    return 1 if prediction == 1 else -1


def save_model():
    check_is_fitted(model)
    joblib.dump(model, MODEL_PATH)
    print(f"AI模型已保存到 {MODEL_PATH.name}")


def load_model():
    global model
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"未找到模型文件 {MODEL_PATH.name}")
    loaded = joblib.load(MODEL_PATH)
    check_is_fitted(loaded)
    model = loaded
    print("AI模型加载成功")

