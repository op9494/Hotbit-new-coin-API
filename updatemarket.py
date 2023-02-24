# Import DictWriter class from CSV module
from csv import DictWriter
from csv import writer
from pandas import *

# list of column names
field_names = ['Date', 'PreviousCount','CurrentCount', 'CoinList','DifferenceList']
launch_field_names = ['Date','CoinList','new_coin']
 
def update_market_data(date, previous_count, current_count,coinlist,differencelist=[]):
    global field_names
    data = { 'Date':date, 'PreviousCount':previous_count,'CurrentCount':current_count, 'CoinList':coinlist,'DifferenceList':differencelist}
    # Open CSV file in append mode
    # Create a file object for this file
    with open('market.csv', 'a', newline='') as csvfile:
        # rdata = read_csv("market.csv")
        # rows = rdata.iloc[-1,3].splitlines()
        # print("fdfs",rows)
        # # Pass the file object and a list
        # # of column names to DictWriter()
        # # You will get a object of DictWriter
        write_obj = DictWriter(csvfile, fieldnames=field_names)
    
        # # Pass the dictionary as an argument to the Writerow()
        write_obj.writerow(data)
    
        # # Close the file object
        csvfile.close()

def update_launchedcoin_data(date,coinlist,newcoin=[]):
    global launch_field_names
    # Open CSV file in append mode
    # Create a file object for this file
    data = { 'Date':date, 'CoinList':coinlist,'new_coin':newcoin}
    with open('launchedcoins.csv', 'a', newline='') as csvfile:
        write_obj = DictWriter(csvfile, fieldnames=launch_field_names)
        write_obj.writerow(data)
        csvfile.close()
