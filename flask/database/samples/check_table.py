import sqlite3

dbname = './RAP_CORPUS.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

# terminalで実行したSQL文と同じようにexecute()に書く
select_sql = 'SELECT * FROM corpus'
for row in cur.execute(select_sql):
    print(row)
# 中身を全て取得するfetchall()を使って、printする。

cur.close()
conn.close()
