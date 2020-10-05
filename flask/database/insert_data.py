import json
import sqlite3
import sys
import pandas as pd

def main():
    dbname = "./rap.db"
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    with open(sys.argv[1], 'r') as fp:
        json_load = json.load(fp)
        print('json_info', json_load)
        for tid, task_info in enumerate(json_load):
            print('json_dump', json.dumps(task_info, indent=4))
            task_info = json.dumps(task_info, indent=4)
            print('tid', tid, 'taskinfo', task_info)
            cur.execute('INSERT INTO task VALUES(?, ?)', (tid, task_info))
    conn.commit()
    cur.close()
    conn.close()
    
if __name__ == '__main__':
    main()
