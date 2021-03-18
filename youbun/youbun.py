import sys
import time
import ccxt
from datetime import datetime
from pprint import pprint
from localmodules import readsetup

print(datetime.now())

# パラメータ###########################################
GOAL = 100000  # [USD]決済価格
LEVE = 1.5  # 維持するレバレッジ
print("deffence", 100 / (LEVE + 1), "%")  # 最高値からこれだけの調整は耐えるよという表示
LOT = 10  # [USD]一度に注文する量
STIME = 3  # [sec]ループ頻度。多分3以上じゃないとだめ
bybit = ccxt.bybit()
bybit.apiKey = readsetup.apikey()
bybit.secret = readsetup.secret()

# 初期処理#########################################
bybit.set_sandbox_mode(True)
# 全注文キャンセル
bybit.cancelAllOrders("BTC/USD")
# 証拠金を取得
res = bybit.fetch_balance()
# ポジションを取得
pos = bybit.v2PrivateGetPositionList({"symbol": "BTCUSD"})
balance = (
    float(res["BTC"]["free"])
    + float(res["BTC"]["used"])
    + float(pos["result"]["unrealised_pnl"])
)
print("balance+unreal:", balance, "BTC")
print("pos", pos["result"]["size"], "USD")
# 決済指値注文
if pos["result"]["size"] > 0:
    order = bybit.v2PrivatePostOrderCreate(
        {
            "side": "Sell",
            "symbol": "BTCUSD",
            "order_type": "Limit",
            "qty": pos["result"]["size"],
            "price": GOAL,
            "time_in_force": "PostOnly",
            "reduce_only": True,
        }
    )


# 寸前のポジション、減ったら決済と認識、停止
pre_pos = pos["result"]["size"]

# 繰り返し################################################
while True:
    try:
        # レバレッジを計算
        pos = bybit.v2PrivateGetPositionList({"symbol": "BTCUSD"})
        margin_leve = float(pos["result"]["effective_leverage"])
        # ポジション量が減ってたら決済スタートor異常事態として終了
        if pos["result"]["size"] < pre_pos:
            print("DECLEASE POS !!!")
            break
        # レバ低ければ買い増
        if margin_leve < LEVE or margin_leve == 100:
            print(datetime.now())
            print("LONG (leve", margin_leve, ")")
            res = bybit.create_market_buy_order("BTC/USD", LOT)

            print("pos", pos["result"]["size"], "USD")
            res = bybit.v2PrivatePostOrderReplace(
                {
                    "order_id": order["result"]["order_id"],
                    "symbol": "BTCUSD",
                    "p_r_qty": pos["result"]["size"] + LOT,
                }
            )
    except Exception as e:
        print(datetime.now())
        print(e)
    time.sleep(STIME)
    pre_pos = pos["result"]["size"]

print("finish")