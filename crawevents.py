from dataclasses import asdict
from datetime import datetime, timezone, timedelta
import json
import re
import argparse

from config import connect
from dry_cursor import DryCursor
from web.local import Local, jp_local

def handle_event(begin, end, name, type_id, type_name, local, cursor, connection):
    sql_get_event = "SELECT id, {start} AS start, {over} AS `over` FROM `Event` WHERE ({start} = %s)".format_map(asdict(local))
    sql_set_event = "UPDATE `Event` SET {start} = %s, {over} = %s WHERE (id = %s)".format_map(asdict(local))
    sql_get_fake_id = "SELECT MAX(fake_id) AS fake_id FROM `Event` WHERE (event_type = %s) GROUP BY event_type"
    sql_ins_event = """INSERT INTO `Event`(`{name}`, `{start}`, `{over}`, 
                       `event_type`, `fake_id`, `event_subtype`) 
                       VALUES(%s, %s, %s, %s, %s, %s)""".format_map(asdict(local))

    print('Start', name)
    cursor.execute(sql_get_event, (begin))
    event = cursor.fetchall()
    if event:
        event = event[0]
        event_id = event['id']
        if event['start'] is None and event['over'] is None:
            print('Edit', name)
            cursor.execute(sql_set_event, (begin, end, event_id))
            connection.commit()
    else:
        print('Insert', name)
        subtype = None
        if type_id == 0:
            subtype = -1
            if re.search('シアター', name):
                subtype = 0
            elif re.search('ツアー', name):
                subtype = 1
            elif re.search('ツインステージ', name):
                subtype = 2
            elif re.search('チューン', name):
                subtype = 3
            elif re.search('テール', name):
                subtype = 4
        cursor.execute(sql_get_fake_id, (type_id))
        fake_id = cursor.fetchall()
        fake_id = 0 if not fake_id else fake_id[0]['fake_id']
        cursor.execute(sql_ins_event, (name, begin, end, type_id, fake_id+1, subtype))
        connection.commit()

def main():
    parser = argparse.ArgumentParser(description='Arguments for crawcards.py')
    parser.add_argument('--real', action="store_true", default=False, help='real run')    
    args = parser.parse_args()

    data = []
    with open('events.json') as f:
        line = f.readline()
        res = re.sub(r'new Date\((\d+)\)', r'\1', line)
        data = json.loads(res)

    connection = connect()
    with connection.cursor() as cursor:
        if not args.real:
            cursor = DryCursor(cursor)
        
        for i in range(len(data)-1, -1, -1):
            event = data[i]

            # 處理活動名稱
            name = event['name'].replace(' ～', '～')
            if name == 'プラチナスターシアタースペシャル～アイドルヒーローズジェネシス～':
                name = 'プラチナスターシアタースペシャル～アイドルヒーローズジェネシス Justice OR Voice～'
            elif name[0:8] == 'エイプリルフール':
                name = name[8:].strip()
                if name == '～アイドルヒーローズ～':
                    name = '出撃！アイドルヒーローズ'
                elif name == '2021(仮)':
                    name = 'ミリ女ファイト！'

            # 處理活動開始、結束時間
            begin = datetime.fromtimestamp(event['beginDate'] / 1000, timezone(timedelta(hours=jp_local.ver_time)))
            end = datetime.fromtimestamp(event['endDate'] / 1000, timezone(timedelta(hours=jp_local.ver_time)))



            event_type = event['type']
            type_name = ''
            if event_type in [3, 4, 10, 11, 12, 13]:
                # PSTイベント
                type_name = 'PST'
                type_id = 0
            elif event_type in [2, 9]:
                # ミリコレ
                type_name = 'ミリコレ'
                type_id = 1
            elif event_type in [5]:
                # 周年イベント
                type_name = '周年'
                type_id = 2
            elif event_type in [6]:
                # WORKING
                type_name = 'WORKING'
                type_id = 3
            elif event_type in [1]:
                # THEATER SHOW TIME
                type_name = 'SHOWTIME'
                type_id = 4
            elif event_type in [7]:
                # その他
                type_name = 'その他'
                type_id = 5
            elif event_type in [14]:
                # TALK PARTY
                type_name = 'TALKPARTY'
                type_id = 6

            if len(type_name) > 0:
                handle_event(begin, end, name, type_id, type_name, jp_local, cursor, connection)
            else:
                print('Event type for', name, 'not found')

if __name__ == '__main__':
    main()
