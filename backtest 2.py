import numpy as np
import pandas as pd

from config import ROUND_TRIP_FEE_RATE, SLIPPAGE_RATE


def run_backtest(dataset, predictions):
    """使用走步测试预测执行简化的只做多回测。"""
    tested = dataset.loc[predictions.index].copy()
    tested = tested.join(predictions)
    tested["position"] = (tested["signal"] == 1).astype(int)
    tested["position_change"] = tested["position"].diff().abs().fillna(tested["position"])

    one_way_cost = ROUND_TRIP_FEE_RATE / 2 + SLIPPAGE_RATE
    tested["strategy_return"] = (
        tested["position"] * tested["future_return"]
        - tested["position_change"] * one_way_cost
    )
    tested["equity"] = (1 + tested["strategy_return"]).cumprod()
    tested["equity_peak"] = tested["equity"].cummax()
    tested["drawdown"] = tested["equity"] / tested["equity_peak"] - 1

    exits = ((tested["position"].shift(1) == 1) & (tested["position"] == 0)).sum()
    entries = ((tested["position"].shift(1).fillna(0) == 0) & (tested["position"] == 1)).sum()
    total_return = float(tested["equity"].iloc[-1] - 1) if not tested.empty else 0.0
    max_drawdown = float(tested["drawdown"].min()) if not tested.empty else 0.0

    active = tested[tested["position"] == 1]
    win_rate = float((active["strategy_return"] > 0).mean()) if not active.empty else 0.0
    returns_std = tested["strategy_return"].std()
    sharpe = 0.0
    if returns_std and not np.isnan(returns_std):
        sharpe = float(tested["strategy_return"].mean() / returns_std * np.sqrt(24 * 365))

    return {
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "entries": int(entries),
        "exits": int(exits),
        "win_rate_per_candle": win_rate,
        "sharpe": sharpe,
        "tested_rows": int(len(tested)),
    }


def format_report(validation, backtest):
    return (
        f"时间序列平衡准确率：{validation['balanced_accuracy']:.2%}\n"
        f"测试K线数量：{backtest['tested_rows']}\n"
        f"回测总收益率：{backtest['total_return']:.2%}\n"
        f"最大回撤：{backtest['max_drawdown']:.2%}\n"
        f"开仓次数：{backtest['entries']}\n"
        f"夏普比率：{backtest['sharpe']:.2f}\n"
        f"持仓K线胜率：{backtest['win_rate_per_candle']:.2%}"
    )

