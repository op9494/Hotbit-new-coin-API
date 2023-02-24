trackingcoin=[]
launchedcoin=[]
newcoin=["PZMr_BTC"]
trackingcoin+=newcoin
print(trackingcoin)
launchedcoin=["PZM2_BTC","PZM3_BTC"]
trackingcoin = [coin for coin in trackingcoin if coin not in launchedcoin]
print(trackingcoin)


