import json
import sqlite3
import sys

def main():
    dbname = "./rap.db"
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    with open(sys.argv[1], 'r') as fp:
        json_load = json.load(fp)
        for tid, task_info in enumerate(json_load):
            print('tid', tid, 'taskinfo', task_info)
            cur.execute('INSERT INTO task VALUES(?, ?)', (tid, str(task_info)))
    conn.commit()
    cur.close()
    conn.close()
    
if __name__ == '__main__':
    main()
