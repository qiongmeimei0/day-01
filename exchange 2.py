import ccxt

from config import (
    HTTP_PROXY,
    LEVERAGE,
    LIVE_TRADING,
    OHLCV_LIMIT,
    OKX_API_KEY,
    OKX_PASSWORD,
    OKX_SANDBOX,
    OKX_SECRET,
    SYMBOL,
    TIMEFRAME,
)


options = {
    "apiKey": OKX_API_KEY,
    "secret": OKX_SECRET,
    "password": OKX_PASSWORD,
    "enableRateLimit": True,
    "options": {"defaultType": "swap"},
}
if HTTP_PROXY:
    options["proxies"] = {"http": HTTP_PROXY, "https": HTTP_PROXY}

exchange = ccxt.okx(options)
if OKX_SANDBOX:
    exchange.set_sandbox_mode(True)


def initialize_exchange():
    """加载市场；实盘模式下检查密钥并设置杠杆。"""
    exchange.load_markets()
    if LIVE_TRADING:
        if not all((OKX_API_KEY, OKX_SECRET, OKX_PASSWORD)):
            raise RuntimeError("实盘模式缺少OKX API配置")
        exchange.set_leverage(LEVERAGE, SYMBOL, params={"mgnMode": "cross"})
        print(f"实盘模式已开启，杠杆 {LEVERAGE}x")
    else:
        print("模拟模式：不会向OKX发送订单")


def fetch_ohlcv():
    return exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=OHLCV_LIMIT)


def fetch_historical_ohlcv(total_candles):
    """按时间向前分页获取历史K线，并去重排序。"""
    timeframe_ms = exchange.parse_timeframe(TIMEFRAME) * 1000
    batch_limit = min(100, OHLCV_LIMIT)
    since = exchange.milliseconds() - total_candles * timeframe_ms
    rows = []

    while len(rows) < total_candles:
        batch = exchange.fetch_ohlcv(
            SYMBOL,
            timeframe=TIMEFRAME,
            since=since,
            limit=min(batch_limit, total_candles - len(rows)),
        )
        if not batch:
            break
        rows.extend(batch)
        next_since = int(batch[-1][0]) + timeframe_ms
        if next_since <= since:
            break
        since = next_since
        if int(batch[-1][0]) >= exchange.milliseconds() - timeframe_ms:
            break

    unique = {int(row[0]): row for row in rows}
    return [unique[key] for key in sorted(unique)][-total_candles:]


def get_contract_size():
    market = exchange.market(SYMBOL)
    return float(market.get("contractSize") or 1.0)


def normalize_amount(amount):
    normalized = float(exchange.amount_to_precision(SYMBOL, amount))
    minimum = exchange.market(SYMBOL).get("limits", {}).get("amount", {}).get("min")
    if minimum is not None and normalized < float(minimum):
        raise ValueError(f"下单数量 {normalized} 小于最小数量 {minimum}")
    return normalized


def fetch_position():
    """返回多头仓位信息；无仓位返回 None。"""
    if not LIVE_TRADING:
        return None
    for position in exchange.fetch_positions([SYMBOL]):
        contracts = float(position.get("contracts") or 0)
        side = position.get("side")
        if position.get("symbol") == SYMBOL and contracts > 0 and side == "long":
            return {
                "contracts": contracts,
                "entry_price": float(position.get("entryPrice") or 0),
            }
    return None


def open_long(amount):
    if not LIVE_TRADING:
        raise RuntimeError("模拟模式禁止真实下单")
    return exchange.create_market_buy_order(
        SYMBOL, normalize_amount(amount), params={"tdMode": "cross"}
    )


def close_long(amount):
    if not LIVE_TRADING:
        raise RuntimeError("模拟模式禁止真实下单")
    return exchange.create_market_sell_order(
        SYMBOL,
        normalize_amount(amount),
        params={"tdMode": "cross", "reduceOnly": True},
    )
