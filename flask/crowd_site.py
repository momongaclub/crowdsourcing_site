from flask import Flask, render_template, request
import pandas as pd
import sqlite3
import random
import string
import datetime
import time

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('hello.html', title='crowdsorcing_site')

@app.route('/input_form', methods = ['POST', 'GET'])
def confirm():
    if request.method == 'POST':
        try:
            dbname = "./database/rap.db"
            conn = sqlite3.connect(dbname, isolation_level='EXCLUSIVE')
            cur = conn.cursor()

            # 指定して時間分引いてそれ以下の古いリザーブを削除する
            limit_time = 60 * 60
            unix_time = time.time()
            old_time = unix_time - limit_time
            cur.execute('DELETE FROM reserve WHERE r_time < ?', (old_time, ))

            # widに紐付けられたtidを取得 取れない場合ももちろんある。
            result = request.form
            wid = result['id']
            cur.execute('SELECT tid FROM reserve WHERE wid = ?', (wid, ))
            tid = cur.fetchone()
            tid = tid[0]
            print('tid', tid)
            
            # workとトランザクションが起きる??

            # まだ完全にテストはできてない
            if tid == None:
                # tidを取得する reserveにそのtidを登録
                # 重複なしかつ回数が少ないものからLIMIT個取得 まだ触ってないtidをこれで取得
                df = pd.read_sql('SELECT task.tid FROM task, \
                                 (SELECT tid, COUNT(*) c FROM work GROUP BY tid) agg_w, \
                                 (SELECT tid, COUNT(*) c FROM reserve GROUP BY tid) agg_r \
                                  WHERE task.tid = agg_w.tid \
                                  AND task.tid = agg_r.tid \
                                  ORDER BY agg_w.c + agg_r.c \
                                  LIMIT 1', conn)
                tid = df['tid'][0]
                cur.execute('INSERT INTO reserve VALUES(?, ?, ?)', (wid, tid, unix_time))
            else:
                cur.execute('UPDATE reserve SET r_time = ? WHERE tid = ? AND wid = ?',
                            (unix_time, tid, wid))

            """ transaction_テスト
            time.sleep(10)
            cur.execute("INSERT INTO work VALUES (?, ?, ?, ?, ?)", (None, 0, 0, 0, 1))
            """

            # task tableからjson取り出しで、renderに渡す情報の準備を
            # tidから引っ張ってくる select task_info from task where tid == ?(tid)
            # 後はjsonから値取り出し作業を行うだけ
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.commit()
            cur.close()
            conn.close()
        return render_template("confirm.html", result=result)
        # return render_template("confirm.html", tid=tid, wid=wid)
        # return render_template("confirm.html", result=result, url=url, s_time=s_time, e_time=e_time)

@app.route('/result', methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        print('result_form', result)
        verses = result['verses']
        url = result['url']
        if len(verses) <= 10:
            print('min_sentence')
            return render_template("result.html", result=result, url=url)
        data = (None, url, verses)
        dbname = "./database/RAP_CORPUS.db"
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute("INSERT INTO corpus VALUES (?, ?, ?)", data)
        conn.commit()
        cur.close()
        conn.close()
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        rancers_key = 'iM'+random_id+'aB'
        return render_template("result.html", result=result, url=url, rancers_key=rancers_key)


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port='18101')
    app.run(debug=True, host='0.0.0.0', port='18101')
