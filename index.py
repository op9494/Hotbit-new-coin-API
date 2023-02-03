import schedule
import time
import requests
import json
from pandas import *
from alarm import triggeralarm
from updatemarket import update_market_data
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
request_adapter = HTTPAdapter(max_retries=3)
session = requests.Session()
session.mount('https://api.hotbit.io', request_adapter)
previouscount = 0
requests.post('https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL',
              json={"msg": "Script is started"})


def getnewcoin(coinlist):
    rdata = read_csv("market.csv")
    pcoinlist = eval(rdata.iloc[-1, 3])
    pc = set(pcoinlist)
    new_coin = [x for x in coinlist if x not in pc]
    return new_coin


def getcoinarray(coinlist):
    coinarray = []
    for coin in coinlist:
        coinarray.append(coin["name"])
    return coinarray


def startCollectidata():
    try:
        global previouscount
        response = session.get('https://api.hotbit.io/api/v1/asset.list')
        jsonresponse = response.json()
        print(time.strftime("%D || %H:%M:%S", time.localtime()), end=" ")
        if response.status_code == 200 and jsonresponse["error"] == None and len(jsonresponse["result"]) > 1:
            currentcount = len(jsonresponse["result"])
            coinlist = jsonresponse["result"]
            coindata = getcoinarray(coinlist)
            if previouscount!=0:
                new_coin = getnewcoin(coindata)
            else:
                new_coin = []

            if previouscount == 0:
                previouscount = currentcount

            if currentcount < previouscount:
                print("Coin removed from hotbit")

            elif currentcount > previouscount:
                triggeralarm()
                requests.post(
                    'https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL', json={'coinname': new_coin})

                print("New coin added to hotbit")
            elif previouscount == currentcount:
                print("No new coin added to hotbit")
            update_market_data(time.strftime("%D || %H:%M:%S", time.localtime(
            )), currentcount, previouscount, coindata, new_coin)

            previouscount = currentcount

    except ConnectionError as ce:
        print(ce)


schedule.every(30).seconds.do(startCollectidata)


while True:
    schedule.run_pending()
    time.sleep(1)
