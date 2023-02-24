import schedule
import time
import requests
import json
from pandas import *
# from alarm import triggeralarm
from updatemarket import update_market_data,update_launchedcoin_data
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
request_adapter = HTTPAdapter(max_retries=3)
session = requests.Session()
session.mount('https://api.hotbit.io', request_adapter)

requests.post('https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL',
             json={"message": "Script is started with new changes"})
previouscount = 0
trackingcoin = []

#This function will return the new coin added to hotbit by comaring the previous list of coin taken from hotbit.
def getnewcoin(coinlist):
    rdata = read_csv("market.csv")
    pcoinlist = eval(rdata.iloc[-1, 3])
    pc = set(pcoinlist)
    new_coin = [x for x in coinlist if x not in pc]
    return new_coin

# This function will return the array of coin which is converted to array of coin symbols 
def getcoinarray(coinlist):
    coinarray = []
    for coin in coinlist:
        coinarray.append(coin["stock"]+"_"+coin["money"])
    return coinarray

# This function will return the array of coin which is converted to array of coin symbols for tracker API 

def getmarketcoinarray(coinlist):
    coinarray = []
    for coin in coinlist:
        coinarray.append(coin["symbol"])
    return coinarray

def startCollectidata():
    try:
        global previouscount
        global trackingcoin
        # To get the asset count in hotbit not listed in the market
        # response = session.get('https://api.hotbit.io/api/v1/asset.list')
        # To get the market count in hotbit listed in the market
        response = session.get('https://api.hotbit.io/api/v1/market.list')
        jsonresponse = response.json()
        print(time.strftime("%D || %H:%M:%S", time.localtime()), end=" ")
        if response.status_code == 200 and jsonresponse["error"] == None and len(jsonresponse["result"]) > 1:
            currentcount = len(jsonresponse["result"])
            coinlist = jsonresponse["result"]
            coindata = getcoinarray(coinlist)
            if previouscount != 0:
                new_coin = getnewcoin(coindata)
            else:
                new_coin = []

            if previouscount == 0:
                previouscount = currentcount

            if currentcount < previouscount:
                print("Coin removed from hotbit")

            elif currentcount > previouscount:
                trackingcoin+=new_coin
                requests.post(
                   'https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL', json={"message":"New coin added to market list ,Soon it will availabe for trade",'coinname': new_coin})
               # triggeralarm()
                print("New coin added to hotbit", new_coin)
            elif previouscount == currentcount:
                print("No new coin added to hotbit")
            update_market_data(time.strftime("%D || %H:%M:%S", time.localtime(
            )), currentcount, previouscount, coindata, new_coin)

            previouscount = currentcount

    except ConnectionError as ce:
        requests.post(
                    'https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL', json={'error': ce,"message":"Error Ocured at syncing with market list"})
        print(ce)

def get_coin_details(coinlist,coin_name):
    coinarray = []
    for coin in coinlist:
        if coin["symbol"]==coin_name:        
            return coin
def isnewcoinlaunched():
    try:
        global trackingcoin
        # To get the market count in hotbit listed in the market
        if len(trackingcoin)>0:
            print(time.strftime("%D || %H:%M:%S", time.localtime()), end=" ")
            response = session.get('https://api.hotbit.io/api/v1/allticker')
            jsonresponse = response.json()
            if response.status_code == 200 and len(jsonresponse["ticker"]) > 1:    
                coinlist = jsonresponse["ticker"]                
                coindata = getmarketcoinarray(coinlist)
                new_coin = [i for i in coindata if i in trackingcoin]
                if len(new_coin)>0:
                    print("New coin Launched:",new_coin)
                    #This will print remove the new coin that is launched already from the trackingcoin array
                    trackingcoin = [coin for coin in trackingcoin if coin not in new_coin]
                    requests.post(
                     'https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL', json={'Action':"Coin Launched in the Hotbit",'coinname': new_coin,'Details':get_coin_details(coinlist,new_coin[0])})
                    update_launchedcoin_data(time.strftime("%D || %H:%M:%S", time.localtime()), coindata, new_coin)
                else:
                    print("Coins on tracking stage:",trackingcoin)
    except ConnectionError as ce:
        requests.post('https://maker.ifttt.com/trigger/new_coin_added/json/with/key/dSVi-LSPxLsmxLEKTI3HxL', json={'error': ce,"message":"Error Ocured at syncing with launched coin"})
        print(ce)


schedule.every(15).seconds.do(startCollectidata)
schedule.every(5).seconds.do(isnewcoinlaunched)

while True:
    schedule.run_pending()
    time.sleep(1)
