import argparse
from config import connect
from dry_cursor import DryCursor


def get_event2card_rows():
    pre_sql_e2c = """SELECT `id`, `EID`, `CID`, `comment`, `type` AS card_type, {type} AS event_type FROM {table}"""

    table_list = ['PSTEventToCard', 'CollectEventToCard', 'AnniversaryToCard', None, None, 'OtherEventToCard', None]
    sql_list = []
    for i in range(len(table_list)):
        if table_list[i] is not None:
            sql_list.append(pre_sql_e2c.format(table=table_list[i], type=i))
    sql_all_e2c = " UNION ALL ".join(sql_list) + " ORDER BY `event_type`, `id`"

    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_all_e2c)
        rows = cursor.fetchall()
    connection.close()
    return rows


def main():
    parser = argparse.ArgumentParser(description='Arguments for move_event2card.py')
    parser.add_argument('--real', action="store_true", default=False, help='real run')    
    args = parser.parse_args()

    events = get_event2card_rows()

    errors = []
    connection = connect()
    with connection.cursor() as cursor:
        sql_get_event_id = """SELECT id FROM `Event` WHERE (event_type = %s AND fake_id = %s)"""
        sql_ins_events = """INSERT INTO `EventToCard`
                            (`EID`, `CID`, `card_type`, `comment`) VALUES(%s, %s, %s, %s)"""

        for e in events:
            cursor.execute(sql_get_event_id, (e['event_type'], e['EID']))
            event_id = cursor.fetchall()
            if not event_id:
                errors.append(e['event_type'] + ' ' + e['EID'] + ' Not Found')
                continue
            event_id = event_id[0]['id']
            e['id'] = event_id
        if not args.real:
            cursor = DryCursor(cursor)
        for e in events:
            cursor.execute(sql_ins_events, (e['id'], e['CID'], e['card_type'], e['comment']))
            connection.commit()
    connection.close()

if __name__ == '__main__':
    main()