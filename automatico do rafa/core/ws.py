import websocket
import json
import time

close_ws = False
result_dict = None

WSS_BASE = "wss://api-v2.blaze.com"


def get_ws_result():
    return result_dict


def set_ws_closed(status):
    global close_ws
    close_ws = status


def on_message(ws, msg):
    global result_dict
    global close_ws
    if "double.tick" in msg:
        result_dict = json.loads(msg[2:])[1]["payload"]

    if close_ws:
        ws.close()


def on_close(ws, close_status_code, msg):
    time.sleep(1)
    connect_websocket()


def on_pong(ws, msg):
    ws.send("2")


def on_open(ws):
    time.sleep(0.1)
    message = '%d["cmd", {"id": "subscribe", "payload": {"room": "double_v2"}}]' % 421
    ws.send(message)


def connect_websocket():
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"{WSS_BASE}/replication/?EIO=3&transport=websocket",
                                on_open=on_open,
                                on_message=on_message,
                                on_close=on_close,
                                on_pong=on_pong
                                )

    ws.run_forever(ping_interval=24,
                   ping_timeout=5,
                   ping_payload="2"
                   )
