from pathlib import Path

import pandas as pd

from config import HISTORICAL_CANDLES
from exchange import fetch_historical_ohlcv, fetch_ohlcv


COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]
DATA_DIR = Path(__file__).with_name("data")
DATA_PATH = DATA_DIR / "ohlcv.csv"


def rows_to_frame(rows):
    return pd.DataFrame(rows, columns=COLUMNS)


def clean_candles(df):
    if df.empty:
        return df
    numeric = ["timestamp", "open", "high", "low", "close", "volume"]
    df = df.copy()
    df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")
    return (
        df.dropna()
        .drop_duplicates("timestamp", keep="last")
        .sort_values("timestamp")
        .tail(HISTORICAL_CANDLES)
        .reset_index(drop=True)
    )


def save_history(df):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    clean_candles(df).to_csv(DATA_PATH, index=False)


def load_or_download_history():
    if DATA_PATH.exists():
        history = pd.read_csv(DATA_PATH)
        recent = rows_to_frame(fetch_ohlcv())
        combined = clean_candles(pd.concat([history, recent], ignore_index=True))
    else:
        print(f"首次启动，下载 {HISTORICAL_CANDLES} 根历史K线...")
        combined = clean_candles(rows_to_frame(fetch_historical_ohlcv(HISTORICAL_CANDLES)))

    # 最后一根可能仍在形成，不用于训练。
    closed = combined.iloc[:-1].copy()
    save_history(combined)
    print(f"历史K线准备完成: {len(closed)} 根已收盘K线")
    return closed


def refresh_history(history):
    recent = rows_to_frame(fetch_ohlcv())
    combined = clean_candles(pd.concat([history, recent], ignore_index=True))
    save_history(combined)
    return combined.iloc[:-1].copy()

