import sys
import codecs
import re
import sqlite3
import pandas as pd
import pprint
import json


START = 2
END = 10
S_T = 0
E_T = 1

def load_urls(fname):
    all_url = []
    with codecs.open(fname, 'r', 'utf-8', 'ignore') as fp:
        header = fp.readline()
        for line in fp:
            urls = []
            line = line.rstrip('\n')
            values = line.split(',')
            for i in range(START, END):
                urls.append(values[i])
                if len(urls) == 2:
                    all_url.append(urls)
                    urls = []
    return all_url


def remove_noise(all_url):
    removed_all_url = []
    for urls in all_url:
        if '' not in urls:
            removed_all_url.append(urls)
    return removed_all_url

def get_time(url):
    pattern = re.compile('\d+')
    start_t = pattern.findall(url[S_T])
    start_t = int(start_t[-1])
    end_t = pattern.findall(url[E_T])
    end_t = int(end_t[-1])
    movie_t = end_t - start_t
    start_t = '{:0=2}:{:0=2}'.format(int(start_t/60), start_t%60)
    end_t = '{:0=2}:{:0=2}'.format(int(end_t/60), end_t%60)
    times = [start_t, end_t, movie_t]
    return times


def main():
    urls = load_urls(sys.argv[1])
    urls = remove_noise(urls)
    data = []
    for url in urls:
        time = get_time(url)
        url.extend(time)
        data.append(url)

    df = pd.DataFrame(data, columns=['s_url', 'e_url', 's_t', 'e_t', 'movie_min'])
    result = df.to_json(orient='records')
    parsed = json.loads(result)
    json_fname = 'umb_urls.json'
    with open(json_fname, 'w') as fp:
        json.dump(parsed, fp, indent=4)
        # json.dumps(parsed, indent=4)
    # pprint.pprint(json.loads(df.to_json(orient='records')), width=40)
    #df.to_json(json_fname ,orient='records')


if __name__ == '__main__':
    main()
