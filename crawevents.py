import pymysql.cursors
from datetime import datetime, date, timezone, timedelta
import json
import re
from config import *

def handle_event(begin, end, name, type, get_sql, set_sql, ins_sql, cursor, connection):
    print('Start', name)
    cursor.execute(get_sql, (begin))
    res = cursor.fetchall()
    if res:
        r = res[0]
        id = r['id']
        if r['start'] is None or r['over'] is None:
            print('Edit', name)
            cursor.execute(set_sql, (begin, end, id))
            connection.commit()
    else:
        print('Insert', name)
        if type == 'PST':
            t_id = -1
            if re.search('シアター', name):
                t_id = 0
            elif re.search('ツアー', name):
                t_id = 1
            elif re.search('ツインステージ', name):
                t_id = 2
            elif re.search('チューン', name):
                t_id = 3
            elif re.search('テール', name):
                t_id = 4
            cursor.execute(ins_sql, (name, t_id, begin, end))
        else:
            cursor.execute(ins_sql, (name, begin, end))
        connection.commit()


def update_astime(events, sql, cursor, connection):
    for e in events:
        if e['asstart'] is None:
            new_start = e['start'].replace(year=e['start'].year + 2)
            new_over = e['over'].replace(year=e['over'].year + 2)
            print('Set asstart, asover for', e['name'])
            cursor.execute(sql, (new_start, new_over, e['id']))
            connection.commit()

def main():
    data = []
    with open('events.json') as f:
        line = f.readline()
        res = re.sub(r'new Date\((\d+)\)', r'\1', line)
        data = json.loads(res)
    
    connection = connect()
    with connection.cursor() as cursor:
        for i in range(len(data)-1, -1, -1):
            d = data[i]
            
            # 處理活動名稱
            name = d['name'].replace(' ～', '～')
            if name == 'プラチナスターシアタースペシャル～アイドルヒーローズジェネシス～':
                name = 'プラチナスターシアタースペシャル～アイドルヒーローズジェネシス Justice OR Voice～'
            elif name[0:8] == 'エイプリルフール':
                name = name[8:].strip()
                if name == '～アイドルヒーローズ～':
                    name = '出撃！アイドルヒーローズ'
            
            # 處理活動開始、結束時間
            begin = datetime.fromtimestamp(d['beginDate'] / 1000, timezone(timedelta(hours=9)))
            end = datetime.fromtimestamp(d['endDate'] / 1000, timezone(timedelta(hours=9)))

            
            type = d['type']
            if type in [2, 9]:
                # ミリコレ
                handle_event(begin, end, name, 'ミリコレ', get_event_col, set_event_col, ins_event_col, cursor, connection)
            elif type in [3, 4, 10, 11, 12, 13]:
                # PSTイベント
                handle_event(begin, end, name, 'PST', get_event_pst, set_event_pst, ins_event_pst, cursor, connection)
            elif type in [6]:
                # WORKING
                handle_event(begin, end, name, 'WORKING', get_event_wkg, set_event_wkg, ins_event_wkg, cursor, connection)
            elif type in [1]:
                # THEATER SHOW TIME
                handle_event(begin, end, name, 'SHOWTIME', get_event_sht, set_event_sht, ins_event_sht, cursor, connection)
            elif type in [5]:
                # 周年イベント
                handle_event(begin, end, name, '周年', get_event_ann, set_event_ann, ins_event_ann, cursor, connection)
            elif type in [7]:
                # その他
                handle_event(begin, end, name, 'その他', get_event_oth, set_event_oth, ins_event_oth, cursor, connection)
        
        cursor.execute(get_event_all_col)
        update_astime(cursor.fetchall(), set_event_col_as, cursor, connection)
        cursor.execute(get_event_all_pst)
        update_astime(cursor.fetchall(), set_event_pst_as, cursor, connection)
        cursor.execute(get_event_all_wkg)
        update_astime(cursor.fetchall(), set_event_wkg_as, cursor, connection)
        cursor.execute(get_event_all_sht)
        update_astime(cursor.fetchall(), set_event_sht_as, cursor, connection)
        cursor.execute(get_event_all_ann)
        update_astime(cursor.fetchall(), set_event_ann_as, cursor, connection)
        cursor.execute(get_event_all_oth)
        update_astime(cursor.fetchall(), set_event_oth_as, cursor, connection)
            

if __name__ == '__main__':
    main()