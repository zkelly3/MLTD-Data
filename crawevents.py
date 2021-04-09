from datetime import datetime, date, timezone, timedelta
import json
import re
from config import connect

def handle_event(begin, end, name, type, local, cursor, connection):
    pre_sql_get_event = "SELECT id, {start} AS start, {over} AS over FROM `{event}` WHERE ({start} = %s)"
    pre_sql_set_event = "UPDATE `{event}` SET {start} = %s, {over} = %s WHERE (id = %s)"
    pre_sql_ins_event = "INSERT INTO `{event}`(`{name}`, `{start}`, `{over}`{other_params}) VALUES(%s, %s, %s{other_vals})"
    
    sql_get_event = pre_sql_get_event.format(**local)
    sql_set_event = pre_sql_set_event.format(**local)
    sql_ins_event = pre_sql_ins_event.format(**local)
    
    print('Start', name)
    cursor.execute(sql_get_event, (begin))
    res = cursor.fetchall()
    if res:
        r = res[0]
        id = r['id']
        if r['start'] is None or r['over'] is None:
            print('Edit', name)
            cursor.execute(sql_set_event, (begin, end, id))
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
            cursor.execute(sql_ins_event, (name, begin, end, t_id))
        else:
            cursor.execute(sql_ins_event, (name, begin, end))
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
            
            local = {
                'name': 'jp_name',
                'start': 'jp_start',
                'over': 'jp_over',
                'ver_time': 9
            }
            
            # 處理活動名稱
            name = d['name'].replace(' ～', '～')
            if name == 'プラチナスターシアタースペシャル～アイドルヒーローズジェネシス～':
                name = 'プラチナスターシアタースペシャル～アイドルヒーローズジェネシス Justice OR Voice～'
            elif name[0:8] == 'エイプリルフール':
                name = name[8:].strip()
                if name == '～アイドルヒーローズ～':
                    name = '出撃！アイドルヒーローズ'
                elif name == '2021(仮)':
                    name = 'ミリ女ファイト！'
            
            # 處理活動開始、結束時間
            begin = datetime.fromtimestamp(d['beginDate'] / 1000, timezone(timedelta(hours=local['ver_time'])))
            end = datetime.fromtimestamp(d['endDate'] / 1000, timezone(timedelta(hours=local['ver_time'])))

            
            event_type = d['type']
            event_type_name = ''
            local['other_params'] = ''
            local['other_vals'] = ''
            if event_type in [2, 9]:
                # ミリコレ
                event_type_name = 'ミリコレ'
                local['event'] = 'CollectEvent'
            elif event_type in [3, 4, 10, 11, 12, 13]:
                # PSTイベント
                event_type_name = 'PST'
                local['event'] = 'PSTEvent'
                local['other_params'] = ', `type`'
                local['other_vals'] = ', %s'
            elif event_type in [6]:
                # WORKING
                event_type_name = 'WORKING'
                local['event'] = 'WorkingEvent'
            elif event_type in [1]:
                # THEATER SHOW TIME
                event_type_name = 'SHOWTIME'
                local['event'] = 'ShowTimeEvent'
            elif event_type in [5]:
                # 周年イベント
                event_type_name = '周年'
                local['event'] = 'Anniversary'
            elif event_type in [7]:
                # その他
                event_type_name = 'その他'
                local['event'] = 'OtherEvent'
            elif event_type in [14]:
                # TALK PARTY
                event_type_name = 'TALKPARTY'
                local['event'] = 'TalkPartyEvent'
            
            if len(event_type_name) > 0:
                handle_event(begin, end, name, event_type_name, local, cursor, connection)
            else:
                print('Event type for', name, 'not found'

if __name__ == '__main__':
    main()