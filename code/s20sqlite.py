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
