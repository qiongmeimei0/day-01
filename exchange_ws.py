import websocket, json
from config import SYMBOL

def on_message(ws, message):
    data = json.loads(message)
    print("WS行情:", data)

def on_error(ws, error):
    print("WS错误:", error)

def on_close(ws):
    print("WS关闭")

def on_open(ws):
    print("WS已连接")
    sub_msg = {
    "op": "subscribe",
    "args":[{"channel":"tickers","instId":SYMBOL}]
    }
    ws.send(json.dumps(sub_msg))

def start_ws():
    ws = websocket.WebSocketApp("wss://ws.okx.com:8443/ws/v5/public",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open)
    ws.run_forever()