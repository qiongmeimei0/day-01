import time
import traceback

import pandas as pd

from ai_model import load_model, predict, save_model, train
from config import LIVE_TRADING, PAPER_BALANCE, POLL_SECONDS, RETRAIN_EVERY_CANDLES
from exchange import (
    close_long,
    fetch_ohlcv,
    fetch_position,
    get_contract_size,
    initialize_exchange,
    normalize_amount,
    open_long,
)
from risk_manager import calculate_position_size, should_stop_loss, should_take_profit


COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def get_closed_candles():
    raw = fetch_ohlcv()
    if len(raw) < 2:
        raise RuntimeError("OKX返回的K线数量不足")
    # 最后一根K线仍可能形成中，不参与训练和交易。
    return pd.DataFrame(raw[:-1], columns=COLUMNS)


def ensure_model(df):
    try:
        load_model()
    except (FileNotFoundError, ValueError, TypeError):
        print("没有可用模型，开始初始训练")
        train(df)
        save_model()


def run():
    initialize_exchange()
    candles = get_closed_candles()
    ensure_model(candles)

    last_candle_timestamp = None
    candles_since_train = 0
    paper_position = None
    print("交易机器人启动成功")

    while True:
        try:
            candles = get_closed_candles()
            candle_timestamp = int(candles["timestamp"].iloc[-1])
            if candle_timestamp == last_candle_timestamp:
                time.sleep(POLL_SECONDS)
                continue

            last_candle_timestamp = candle_timestamp
            candles_since_train += 1
            current_price = float(candles["close"].iloc[-1])

            if candles_since_train >= RETRAIN_EVERY_CANDLES:
                train(candles)
                save_model()
                candles_since_train = 0

            signal = predict(candles)
            position = fetch_position() if LIVE_TRADING else paper_position
            contract_size = get_contract_size()
            amount = calculate_position_size(PAPER_BALANCE, current_price, contract_size)
            amount = normalize_amount(amount)

            print(
                f"K线时间={pd.to_datetime(candle_timestamp, unit='ms', utc=True)}, "
                f"价格={current_price}, AI信号={signal}, 持仓={bool(position)}"
            )

            # 先处理已有仓位的止损、止盈和反向信号。
            if position:
                entry_price = float(position["entry_price"])
                exit_reason = None
                if should_stop_loss(entry_price, current_price):
                    exit_reason = "止损"
                elif should_take_profit(entry_price, current_price):
                    exit_reason = "止盈"
                elif signal == -1:
                    exit_reason = "AI卖出信号"

                if exit_reason:
                    held_amount = float(position["contracts"])
                    if LIVE_TRADING:
                        close_long(held_amount)
                    else:
                        paper_position = None
                    print(f"{exit_reason}平仓: {held_amount} 张，价格 {current_price}")

            elif signal == 1:
                if LIVE_TRADING:
                    open_long(amount)
                else:
                    paper_position = {
                        "contracts": amount,
                        "entry_price": current_price,
                    }
                print(f"开多仓: {amount} 张，价格 {current_price}")

            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            print("程序已停止")
            break
        except Exception:
            traceback.print_exc()
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()

