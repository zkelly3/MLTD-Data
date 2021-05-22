from datetime import datetime, date, timezone, timedelta
import json
import re
from config import connect

def main():
    pre_get_all_targets = """SELECT id, jp_name AS name, jp_start, jp_over, as_start, as_over FROM `{target}`
                             WHERE jp_name IS NOT NULL AND as_name IS NOT NULL AND jp_start IS NOT NULL AND as_start IS NULL"""
    pre_set_as_time = "UPDATE `{target}` SET as_start = %s, as_over = %s WHERE (id = %s)"

    todos = [{'name': '白金轉蛋', 'target': 'Gasha'},
        {'name': '活動', 'target': 'Event'}]

    connection = connect()
    with connection.cursor() as cursor:
        for todo in todos:
            print('開始處理' + todo['name'])
            get_all_targets = pre_get_all_targets.format(target=todo['target'])
            set_as_time = pre_set_as_time.format(target=todo['target'])

            cursor.execute(get_all_targets)
            targets = cursor.fetchall()
            for tgt in targets:
                new_start = tgt['jp_start'].replace(year=tgt['jp_start'].year + 2)
                new_over = tgt['jp_over'].replace(year=tgt['jp_over'].year + 2) if tgt['jp_over'] is not None else None
                print('Update as_start, as_over for', tgt['name'], new_start, new_over)
                cursor.execute(set_as_time, (new_start, new_over, tgt['id']))
                connection.commit()
    connection.close()

if __name__ == '__main__':
    main()