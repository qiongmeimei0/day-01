import time
import traceback
import pandas as pd
from exchange import fetch_ohlcv, fetch_position, limit_buy, limit_sell
from strategy import generate_signal
from risk_manager import calculate_position_size, should_stop_loss, should_take_profit
from ai_model import train, predict, save_model, load_model, add_indicators

# 参数
BALANCE = 100       # 示例资金
N_TRAIN = 100        # 每100根K线训练一次
last_train_len = 0   # 上次训练的数据长度

# 启动时加载模型，如果没有则训练一次
try:
    load_model()
    print("AI模型加载成功")
except:
    print("第一次启动，训练初始模型")
    df_init = pd.DataFrame(fetch_ohlcv(), columns=['timestamp','open','high','low','close','volume'])
    df_init = add_indicators(df_init)
    train(df_init)
    save_model()
    last_train_len = len(df_init)
    print("初始AI模型训练完成并保存")

print("项目启动成功")

while True:
    try:
        # 获取最新K线
        df = pd.DataFrame(fetch_ohlcv(), columns=['timestamp','open','high','low','close','volume'])
        df = add_indicators(df)
        print(df)

        # ---- 滚动训练 ----
        if len(df) - last_train_len >= N_TRAIN:
            print("新增K线达到阈值，训练AI模型...")
            train(df)
            save_model()
            last_train_len = len(df)
            print("AI模型训练完成并已保存")

        # ---- AI预测 ----
        signal = predict(df)

        # ---- 当前仓位与价格 ----
        position = fetch_position()
        price = df['close'].iloc[-1]
        size = calculate_position_size(BALANCE, price)

        # ---- 执行交易 ----
        if signal == 1 and not position:
#            limit_buy(size, price)
            print("买入", size, price)
        elif signal == -1 and position:
#            limit_sell(size, price)
            print("卖出", size, price)

        # ---- 止盈止损 ----
        if position:
            if should_stop_loss(price, df['close'].iloc[-1]):
#                limit_sell(size, price)
                print("止损平仓")
            elif should_take_profit(price, df['close'].iloc[-1]):
#                limit_sell(size, price)
                print("止盈平仓")

        time.sleep(60)

    except Exception as e:
        traceback.print_exc()
        time.sleep(5)
