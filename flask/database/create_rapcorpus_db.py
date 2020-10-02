import sqlite3

# TEST.dbを作成する
# すでに存在していれば、それにアクセスする。
dbname = 'RAP_CORPUS.db'
conn = sqlite3.connect(dbname)

# sqliteを操作するカーソルオブジェクト
cur = conn.cursor()

cur.execute(
    '''CREATE TABLE corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, url STRING, verses text)''')

    # 'CREATE TABLE corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, url STRING, verses STRING)')
# データベースへコミット。これで変更が反映される。
conn.commit()

cur.close()
# データベースへのコネクションを閉じる。(必須)
conn.close()
