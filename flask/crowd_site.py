from flask import Flask, render_template, request
import pandas as pd
import sqlite3
import random
import string
import datetime
import time
import json

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

            limit_time = 60 * 60
            unix_time = time.time()
            old_time = unix_time - limit_time
            cur.execute('DELETE FROM reserve WHERE r_time < ?', (old_time, ))

            result = request.form
            wid = result['id']
            cur.execute('SELECT tid FROM reserve WHERE wid = ?', (wid, ))
            tid = cur.fetchone()

            if tid == None: # wid is not in the reserve table
                df = pd.read_sql('SELECT task.tid, \
                                  CASE WHEN agg_w.c IS NULL THEN 0 ELSE agg_w.c END AS wc, \
                                  CASE WHEN agg_r.c IS NULL THEN 0 ELSE agg_r.c END AS rc \
                                  FROM task LEFT JOIN \
                                 (SELECT tid, COUNT(*) c FROM work GROUP BY tid) agg_w \
                                  ON task.tid = agg_w.tid LEFT JOIN \
                                 (SELECT tid, COUNT(*) c FROM reserve GROUP BY tid) agg_r \
                                  ON task.tid = agg_r.tid ORDER BY wc + rc LIMIT 1', conn)
                tid = df['tid'][0]
                cur.execute('INSERT INTO reserve VALUES(?, ?, ?)', (wid, tid, unix_time))
            else:
                tid = tid[0]
                cur.execute('UPDATE reserve SET r_time = ? WHERE tid = ? AND wid = ?',
                            (unix_time, tid, wid))
            cur.execute('SELECT task.task_info FROM task WHERE task.tid = ?', (tid, ))
            task_info = cur.fetchone()
            print('task_info_fetchone', task_info)

            # print(pd.read_json(task_info[0].replace("'", '"')))

            task_info = '"' + task_info[0] + '"'
            # task_info = "'" + task_info[0] + "'"
            print('task_info', task_info)
            print('task_info_json_type', type(json.loads(task_info)))
            task_info_json = json.loads(task_info)
            print('task_info_json', type(task_info))
            # print(task_info_json['e_time'])
            # s_url, e_url, s_t, e_t, movie_min

            # TODO To get json of taskinfo by table. next, its send a taskinfo to render
            # select task_info from task where tid == ?(tid)
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.commit()
            cur.close()
            conn.close()
        # return render_template("confirm.html", result=result)
        # return render_template("confirm.html", tid=tid, wid=wid)
        return render_template("confirm.html", result=result, url=task_info_json['s_url'], s_time=task_info_json['s_t'], e_time=task_info_json['e_t'])

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
