from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import talib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.utils.validation import check_is_fitted

from config import CONFIDENCE_THRESHOLD, MIN_MOVE_THRESHOLD, TIME_SERIES_SPLITS


FEATURES = [
    "rsi",
    "macd",
    "macd_hist",
    "atr_pct",
    "bb_position",
    "ema_spread",
    "return_1",
    "return_3",
    "return_6",
    "volatility_24",
    "volume_change",
    "range_pct",
]
MODEL_PATH = Path(__file__).with_name("rf_model.pkl")
MIN_TRAIN_ROWS = 500
MODEL_VERSION = 2


def new_model():
    return RandomForestClassifier(
        n_estimators=400,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )


model = new_model()


def add_indicators(df):
    """为K线添加趋势、动量、波动和成交量特征。"""
    required = {"open", "high", "low", "close", "volume"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"K线缺少字段: {sorted(missing)}")

    result = df.copy().sort_values("timestamp").drop_duplicates("timestamp")
    close = result["close"].astype(float)
    high = result["high"].astype(float)
    low = result["low"].astype(float)
    volume = result["volume"].astype(float)

    result["rsi"] = talib.RSI(close, timeperiod=14)
    result["macd"], result["macd_signal"], result["macd_hist"] = talib.MACD(
        close, fastperiod=12, slowperiod=26, signalperiod=9
    )
    atr = talib.ATR(high, low, close, timeperiod=14)
    result["atr_pct"] = atr / close

    upper, middle, lower = talib.BBANDS(close, timeperiod=20)
    band_width = (upper - lower).replace(0, np.nan)
    result["bb_position"] = (close - lower) / band_width

    ema_fast = talib.EMA(close, timeperiod=12)
    ema_slow = talib.EMA(close, timeperiod=26)
    result["ema_spread"] = (ema_fast - ema_slow) / close

    result["return_1"] = close.pct_change(1)
    result["return_3"] = close.pct_change(3)
    result["return_6"] = close.pct_change(6)
    result["volatility_24"] = result["return_1"].rolling(24).std()
    result["volume_change"] = volume.pct_change().replace([np.inf, -np.inf], np.nan)
    result["range_pct"] = (high - low) / close

    return result.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)


def prepare_dataset(df):
    """使用下一根K线净变动生成 -1/0/1 标签。"""
    prepared = add_indicators(df)
    prepared["future_return"] = prepared["close"].shift(-1) / prepared["close"] - 1
    prepared["target"] = 0
    prepared.loc[prepared["future_return"] > MIN_MOVE_THRESHOLD, "target"] = 1
    prepared.loc[prepared["future_return"] < -MIN_MOVE_THRESHOLD, "target"] = -1
    return prepared.iloc[:-1].copy()


def signal_from_probabilities(classes, probabilities):
    index = int(np.argmax(probabilities))
    predicted_class = int(classes[index])
    confidence = float(probabilities[index])
    signal = predicted_class if confidence >= CONFIDENCE_THRESHOLD else 0
    probability_map = {int(cls): float(prob) for cls, prob in zip(classes, probabilities)}
    return signal, confidence, probability_map


def walk_forward_evaluate(dataset):
    """按时间顺序训练/测试，并返回测试预测，避免未来数据泄漏。"""
    splitter = TimeSeriesSplit(n_splits=TIME_SERIES_SPLITS, gap=1)
    predictions = []
    fold_scores = []

    for fold, (train_idx, test_idx) in enumerate(splitter.split(dataset), start=1):
        train_part = dataset.iloc[train_idx]
        test_part = dataset.iloc[test_idx]
        fold_model = new_model()
        fold_model.fit(train_part[FEATURES], train_part["target"])

        probabilities = fold_model.predict_proba(test_part[FEATURES])
        fold_signals = []
        for row in probabilities:
            signal, confidence, probability_map = signal_from_probabilities(
                fold_model.classes_, row
            )
            fold_signals.append(signal)
            predictions.append(
                {
                    "index": int(test_part.index[len(fold_signals) - 1]),
                    "signal": signal,
                    "confidence": confidence,
                    "probability_up": probability_map.get(1, 0.0),
                    "probability_down": probability_map.get(-1, 0.0),
                    "probability_flat": probability_map.get(0, 0.0),
                }
            )

        fold_score = balanced_accuracy_score(test_part["target"], fold_signals)
        fold_scores.append(float(fold_score))
        print(f"时间序列验证第 {fold} 折平衡准确率: {fold_score:.2%}")

    prediction_df = pd.DataFrame(predictions).set_index("index").sort_index()
    return {
        "balanced_accuracy": float(np.mean(fold_scores)),
        "fold_scores": fold_scores,
        "predictions": prediction_df,
    }


def train(df):
    """先做走步验证，再使用全部历史数据训练最终模型。"""
    global model
    dataset = prepare_dataset(df)
    if len(dataset) < MIN_TRAIN_ROWS:
        raise ValueError(f"有效K线不足，需要至少 {MIN_TRAIN_ROWS} 根")
    if dataset["target"].nunique() < 2:
        raise ValueError("训练标签不足两类，无法训练分类模型")

    evaluation = walk_forward_evaluate(dataset)
    model = new_model()
    model.fit(dataset[FEATURES], dataset["target"])
    evaluation["dataset"] = dataset
    print(f"最终模型训练完成，样本数: {len(dataset)}")
    return evaluation


def predict(df):
    """返回交易信号、置信度和各类别概率。"""
    check_is_fitted(model)
    prepared = add_indicators(df)
    if prepared.empty:
        raise ValueError("指标计算后没有可用于预测的K线")
    probabilities = model.predict_proba(prepared[FEATURES].iloc[-1:])[0]
    signal, confidence, probability_map = signal_from_probabilities(
        model.classes_, probabilities
    )
    return {
        "signal": signal,
        "confidence": confidence,
        "probability_up": probability_map.get(1, 0.0),
        "probability_down": probability_map.get(-1, 0.0),
        "probability_flat": probability_map.get(0, 0.0),
    }


def save_model():
    check_is_fitted(model)
    joblib.dump(
        {"version": MODEL_VERSION, "features": FEATURES, "model": model}, MODEL_PATH
    )
    print(f"AI模型已保存到 {MODEL_PATH.name}")


def load_model():
    global model
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"未找到模型文件 {MODEL_PATH.name}")
    payload = joblib.load(MODEL_PATH)
    if not isinstance(payload, dict) or payload.get("version") != MODEL_VERSION:
        raise ValueError("模型版本已过期，需要重新训练")
    if payload.get("features") != FEATURES:
        raise ValueError("模型特征与当前代码不一致，需要重新训练")
    loaded = payload["model"]
    check_is_fitted(loaded)
    model = loaded
    print("AI模型加载成功")
