from config import MAX_POSITION_USDT, RISK_PER_TRADE, STOP_LOSS, TAKE_PROFIT


def calculate_position_size(balance, price, contract_size=1.0):
    """按照最大亏损比例计算合约张数，并限制最大名义价值。"""
    if balance <= 0 or price <= 0 or contract_size <= 0:
        raise ValueError("余额、价格和合约面值必须大于0")

    risk_amount = balance * RISK_PER_TRADE
    risk_based_contracts = risk_amount / (price * STOP_LOSS * contract_size)
    cap_based_contracts = MAX_POSITION_USDT / (price * contract_size)
    return min(risk_based_contracts, cap_based_contracts)


def should_stop_loss(entry_price, current_price):
    return current_price <= entry_price * (1 - STOP_LOSS)


def should_take_profit(entry_price, current_price):
    return current_price >= entry_price * (1 + TAKE_PROFIT)

