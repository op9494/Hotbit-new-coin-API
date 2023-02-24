import schedule
import time
import requests
import json
from pandas import *
# from alarm import triggeralarm
from updatemarket import update_market_data
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
request_adapter = HTTPAdapter(max_retries=3)
session = requests.Session()
session.mount('https://api.hotbit.io', request_adapter)
previouscount = 0
requests.post('https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL',
              json={"message": "Script is started with new changes"})


def getnewcoin(coinlist):
    rdata = read_csv("market.csv")
    pcoinlist = eval(rdata.iloc[-1, 3])
    pc = set(pcoinlist)
    new_coin = [x for x in coinlist if x not in pc]
    return new_coin


def getremovedcoin(coinlist):
    rdata = read_csv("market.csv")
    pcoinlist = eval(rdata.iloc[-1, 3])
    pc = set(pcoinlist)
    removed_coin = [x for x in pc if x not in coinlist]
    return removed_coin

def getcoinarray(coinlist):
    coinarray = []
    for coin in coinlist:
        coinarray.append(coin["symbol"])
    return coinarray


def startCollectidata():
    try:
        global previouscount
        # To get the asset count in hotbit not listed in the market
        # response = session.get('https://api.hotbit.io/api/v1/asset.list')
        # To get the market count in hotbit listed in the market
        response = session.get('https://api.hotbit.io/api/v1/allticker')
        jsonresponse = response.json()
        print(time.strftime("%D || %H:%M:%S", time.localtime()), end=" ")
        if response.status_code == 200 and len(jsonresponse["ticker"]) > 1:
            currentcount = len(jsonresponse["ticker"])
            coinlist = jsonresponse["ticker"]
            coindata = getcoinarray(coinlist)
            if previouscount != 0:
                new_coin = getnewcoin(coindata)
            else:
                new_coin = []

            if previouscount == 0:
                previouscount = currentcount
                update_market_data(time.strftime("%D || %H:%M:%S", time.localtime(
                )), currentcount, previouscount, coindata, new_coin)

            if currentcount < previouscount:
                removed_coin = getremovedcoin(coindata)
                requests.post(
                    'https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL', json={'Action':"Coin removed from hot bit",'coinname': removed_coin})
                update_market_data(time.strftime("%D || %H:%M:%S", time.localtime(
                )), currentcount, previouscount, coindata, removed_coin)
                print("Coin removed from hotbit", removed_coin)

            elif currentcount > previouscount:
                requests.post(
                    'https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL', json={'Action':"Coin Added to hot bit",'coinname': new_coin})
               # triggeralarm()
                update_market_data(time.strftime("%D || %H:%M:%S", time.localtime(
                )), currentcount, previouscount, coindata, new_coin)
                print("New coin added to hotbit", new_coin)
            elif previouscount == currentcount:
                print("No new coin added to hotbit")
            previouscount = currentcount

    except ConnectionError as ce:
        requests.post(
            'https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL', json={'error': ce})

        print(ce)


def sendako():
    requests.post('https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL',
                  json={'Status': "dev server is running successfully"})


schedule.every(10).seconds.do(startCollectidata)
schedule.every(60).minutes.do(sendako)

while True:
    schedule.run_pending()
    time.sleep(1)
