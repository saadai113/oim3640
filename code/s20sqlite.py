import sqlite3

from code.stocks import db

conn = sqlite3.connect('towns.db')
conn.execute('''CREATE TABLE IF NOT EXISTS towns
                (name TEXT, county TEXT, pop INTEGER)''')
conn.execute('INSERT INTO towns VALUES (?, ?, ?)',
             ('Boston', 'Suffolk', 675647))
conn.commit()

for row in conn.execute('SELECT * FROM towns'):
    print(row)  # ('Boston', 'Suffolk', 675647)

def display_portfolio():
    cursor=db.cursor()
    with sqlite 3.connect('portfolio.db') as conn:
        for row in conn.execute('SELECT * FROM portfolio'):
            print(row)

def display_expensive_stocks(threshold_price):
    with sqlite3.connect("data/stocks.db") as db:
        cursor=db.cursor()
        results=curosor.execute('SELECT * FROM stocks WHERE price > ?', (threshold_price,))
        for row in results:
            print(row)
