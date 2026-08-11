import json

import websocket

from config import OKX_WS_INST_ID


def on_message(ws, message):
    print("WS行情:", json.loads(message))


def on_error(ws, error):
    print("WS错误:", error)


def on_close(ws, close_status_code, close_msg):
    print("WS关闭:", close_status_code, close_msg)


def on_open(ws):
    print("WS已连接")
    ws.send(
        json.dumps(
            {
                "op": "subscribe",
                "args": [{"channel": "tickers", "instId": OKX_WS_INST_ID}],
            }
        )
    )


def start_ws():
    ws = websocket.WebSocketApp(
        "wss://ws.okx.com:8443/ws/v5/public",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever()


if __name__ == "__main__":
    start_ws()

