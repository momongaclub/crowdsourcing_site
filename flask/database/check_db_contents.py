import sqlite3

dbname = 'rap.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

# terminalで実行したSQL文と同じようにexecute()に書く
cur.execute('SELECT * FROM reserve')
print('reserve')
print(cur.fetchall())
cur.execute('SELECT * FROM task')
print('task')
print(cur.fetchall())
cur.execute('SELECT * FROM work')
print('work')
print(cur.fetchall())

cur.close()
conn.close()
