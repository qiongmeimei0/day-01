from config import STOP_LOSS, TAKE_PROFIT, RISK_PER_TRADE

def calculate_position_size(balance, price):
    # 根据风险比例计算仓位
    risk_amount = balance * RISK_PER_TRADE
    return risk_amount / (price * STOP_LOSS)

def should_stop_loss(entry_price, current_price):
    # 判断是否止损
    return current_price <= entry_price * (1-STOP_LOSS)

def should_take_profit(entry_price, current_price):
    # 判断是否止盈
    return current_price >= entry_price * (1+TAKE_PROFIT)