from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import sqlite3

import random
import string
import json
import time

# app = Flask(__name__)
app = Flask(__name__,
            static_url_path='',
            static_folder='static')


@app.route('/')
def home():
    return render_template('index.html', title='crowdsorcing_site')


@app.route('/input_form', methods=['POST', 'GET'])
def input_form():
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

            if tid is None:
                # wid is not in the reserve table
                """
                df = pd.read_sql('SELECT task.tid, \
                                  CASE WHEN agg_w.c IS NULL THEN 0 \
                                  ELSE agg_w.c END AS wc, \
                                  CASE WHEN agg_r.c IS NULL THEN 0 \
                                  ELSE agg_r.c END AS rc \
                                  FROM task LEFT JOIN \
                                 (SELECT tid, COUNT(*) c FROM work \
                                  GROUP BY tid) agg_w \
                                  ON task.tid = agg_w.tid LEFT JOIN \
                                 (SELECT tid, COUNT(*) c FROM reserve \
                                  GROUP BY tid) agg_r \
                                  ON task.tid = agg_r.tid ORDER BY wc + rc \
                                  LIMIT 1', conn)
                WHERE task.tid != (select tid from work where work.wid = " + wid + "" "mina_nagai") \
                """

                df = pd.read_sql('SELECT task.tid, CASE WHEN agg_w.c IS NULL THEN 0 \
ELSE agg_w.c END AS wc, CASE WHEN agg_r.c IS NULL THEN 0 \
ELSE agg_r.c END AS rc, \
CASE WHEN work_ex.wid IS NULL THEN 0 ELSE work_ex.wid END AS wid_ex \
FROM task LEFT JOIN (SELECT tid, COUNT(*) c FROM work GROUP BY tid) agg_w ON task.tid = agg_w.tid LEFT JOIN (SELECT tid, COUNT(*) c FROM reserve GROUP BY tid) agg_r ON task.tid = agg_r.tid \
LEFT JOIN (SELECT tid, wid FROM work) work_ex ON task.tid = work_ex.tid \
WHERE task.tid != (select tid from work where work.wid = "' + wid + '") \
OR task.tid NOT IN (SELECT tid FROM work WHERE work.wid = "' + wid + '") \
GROUP BY task.tid \
ORDER BY wc + rc LIMIT 1', conn)
                print('tid:', df['tid'])
                tid = df['tid'][0]
                cur.execute('INSERT INTO reserve VALUES(?, ?, ?)', (wid, tid, unix_time))
            else:
                tid = tid[0]
                cur.execute('UPDATE reserve SET r_time = ? WHERE tid = ? AND wid = ?',
                            (unix_time, tid, wid))

            cur.execute('SELECT task.task_info FROM task WHERE task.tid = ?', (tid, ))
            task_info = cur.fetchone()
            task_info = task_info[0]
            task_info_json = json.loads(task_info)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.commit()
            cur.close()
            conn.close()
        return render_template("input_form.html", result=result, url=task_info_json['s_url'], s_time=task_info_json['s_t'], e_time=task_info_json['e_t'], worker_id=wid, task_id=tid)


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        data = (result['worker_id'], result['task_id'], result['verses'], 'null', 'null')
        dbname = "./database/rap.db"
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        # taskidとwidからreserveのr_timeを取得
        cur.execute('SELECT r_time FROM reserve WHERE tid = ? AND wid = ?', (result['task_id'], result['worker_id']))
        r_time = cur.fetchone()[0]
        task_time = int(time.time() - r_time)
        cur.execute('INSERT INTO work VALUES (?, ?, ?, ?, ?)', data)
        # After registration, delete data from reserve
        cur.execute('DELETE FROM reserve WHERE tid = ? AND wid = ?', (result['task_id'], result['worker_id'] ))
        conn.commit()
        cur.close()
        conn.close()
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        rancers_key = str(task_time)+'iM'+random_id+'aB'
        return render_template("result.html", result=result, url=result['url'], rancers_key=rancers_key)


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port='18101')
    app.run(debug=True, host='0.0.0.0', port='18101')
