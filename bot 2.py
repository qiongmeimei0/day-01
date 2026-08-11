import time
import traceback

import pandas as pd

from ai_model import load_model, predict, save_model, train
from backtest import format_report, run_backtest
from config import LIVE_TRADING, PAPER_BALANCE, POLL_SECONDS, RETRAIN_EVERY_CANDLES
from exchange import (
    close_long,
    fetch_position,
    get_contract_size,
    initialize_exchange,
    normalize_amount,
    open_long,
)
from market_data import load_or_download_history, refresh_history
from notifier import send_notification
from risk_manager import calculate_position_size, should_stop_loss, should_take_profit


def train_and_report(candles, title):
    evaluation = train(candles)
    backtest = run_backtest(evaluation["dataset"], evaluation["predictions"])
    save_model()
    report = format_report(evaluation, backtest)
    print(report)
    send_notification(title, report)
    return evaluation, backtest


def ensure_model(candles):
    try:
        load_model()
    except (FileNotFoundError, ValueError, TypeError):
        print("没有可用模型，开始初始训练和走步回测")
        train_and_report(candles, "AI初始训练与回测完成")


def run():
    initialize_exchange()
    candles = load_or_download_history()
    ensure_model(candles)

    last_candle_timestamp = None
    candles_since_train = 0
    paper_position = None
    print("交易机器人启动成功")

    while True:
        try:
            candles = refresh_history(candles)
            candle_timestamp = int(candles["timestamp"].iloc[-1])
            if candle_timestamp == last_candle_timestamp:
                time.sleep(POLL_SECONDS)
                continue

            last_candle_timestamp = candle_timestamp
            candles_since_train += 1
            current_price = float(candles["close"].iloc[-1])

            if candles_since_train >= RETRAIN_EVERY_CANDLES:
                train_and_report(candles, "AI定期训练与回测完成")
                candles_since_train = 0

            prediction = predict(candles)
            signal = prediction["signal"]
            confidence = prediction["confidence"]
            position = fetch_position() if LIVE_TRADING else paper_position
            contract_size = get_contract_size()
            amount = calculate_position_size(PAPER_BALANCE, current_price, contract_size)
            amount = normalize_amount(amount)

            print(
                f"K线时间={pd.to_datetime(candle_timestamp, unit='ms', utc=True)}, "
                f"价格={current_price}, 信号={signal}, 置信度={confidence:.2%}, "
                f"上涨={prediction['probability_up']:.2%}, "
                f"下跌={prediction['probability_down']:.2%}, "
                f"观望={prediction['probability_flat']:.2%}, 持仓={bool(position)}"
            )

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
                    pnl_pct = (current_price / entry_price - 1) * 100
                    if LIVE_TRADING:
                        close_long(held_amount)
                    else:
                        paper_position = None
                    print(f"{exit_reason}平仓: {held_amount} 张，价格 {current_price}")
                    send_notification(
                        f"{exit_reason}平仓",
                        f"模式：{'实盘' if LIVE_TRADING else '模拟'}\n"
                        f"开仓价：{entry_price}\n平仓价：{current_price}\n"
                        f"数量：{held_amount} 张\n收益率：{pnl_pct:.2f}%",
                    )

            elif signal == 1:
                if LIVE_TRADING:
                    open_long(amount)
                else:
                    paper_position = {
                        "contracts": amount,
                        "entry_price": current_price,
                    }
                print(f"开多仓: {amount} 张，价格 {current_price}")
                send_notification(
                    "开多仓",
                    f"模式：{'实盘' if LIVE_TRADING else '模拟'}\n"
                    f"价格：{current_price}\n数量：{amount} 张\n"
                    f"置信度：{confidence:.2%}",
                )
            else:
                print("观望：置信度不足或模型判断为中性")

            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            print("程序已停止")
            break
        except Exception:
            traceback.print_exc()
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()

