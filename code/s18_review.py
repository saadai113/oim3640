import yfinance as yf
from pprint import pprint
#create a dictionary with the current price of each stock
tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
stocks = {}

for t in tickers:
    stocks[t]= yf.Ticker(t).info['currentPrice']

print(stocks)

def sort_by_price(t):
    return t[1]
print('After sorting...')
print(sorted(stocks.items(), key=lambda t: t[1]))

a=[('c', 1), ('d', 2), ('c', 3), ('e', 4), ('d', 5)]
print(sorted(a, key=sort_by_price))

names=['Charlie', 'Alice', 'Bob', '124', 'Eve']
uppercase_names=[]

for name in names:
    try:
        print(name.upper())
        uppercase_names.append(name.upper())
    except AttributeError:
        print(f"Error: {name} is not a string and cannot be converted to uppercase.")
print("Uppercase names:",  uppercase_names)

import requests
response=requests.get('https://oim.108122.xyz/mass', headers={"X-Token": "auroraaurora"},)

data=response.json()
print(len(data))
print(data.keys())
towns=data['data']
print(type(towns))
print(len(towns))
