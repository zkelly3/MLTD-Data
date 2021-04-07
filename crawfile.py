import json
import requests
import re
from bs4 import BeautifulSoup
#import pymysql.cursors
from datetime import datetime
#from config import *

def bs4_data(url, *args, **kwargs):
    rq = requests.get(url)
    rq.encoding = 'utf-8'
    soup = BeautifulSoup(rq.text,"html.parser")
    res = soup.find_all(*args, **kwargs)
    
    return res

def handle(url):
    span = bs4_data(url, string=re.compile('.*イベント:.*'))
    if span:
        words = span[0].parent.text
        if re.search('プラチナスター', words):
            print('PST')
        elif re.search('ミリコレ', words):    
            print('百萬收藏')
        elif re.search('エイプリルフール', words):
            print('其他')
        else:
            print('周年')
        return
        
    
    span = bs4_data(url, string=re.compile('.*ガシャ種別:.*'))
    if span:
        words = span[0].parent.text
        if re.search('恒常', words):
            print('常駐')
        elif re.search('期間限定', words):
            print('期間限定')
        elif re.search('フェス限定', words):
            print('FES')
        else:
            print('特殊抽卡')
        return
    
    print('其他')

def consume(s, prefix):
    if not s.startswith(prefix):
        return False, None
    else:
        return True, s[len(prefix):].strip()

def main():
    '''
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(get_event_all_col)
        res = cursor.fetchall()
        for e in res:
            print(e['jp_start'], e['jp_start'].replace(year=e['jp_start'].year +2))
    '''
    res = bs4_data('https://mltd.matsurihi.me/cards/1108', 'span', string='ダンス')
    for r in res:
        has_value, value = consume(r.parent.text, 'ダンス')
        if has_value:    
            print(int(value.split('(')[0].strip()))
    
    

if __name__ == '__main__':
    main()