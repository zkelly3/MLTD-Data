import argparse
from config import connect
from dry_cursor import DryCursor


def get_all_events():
    pre_sql_events = """SELECT id, jp_name, as_name, 
                        jp_start, jp_over, as_start, as_over,
                        type AS event_subtype, {type} AS event_type, comment FROM {table}"""

    table_list = ['PSTEvent', 'CollectEvent', 'Anniversary', 'WorkingEvent', 'ShowTimeEvent', 'OtherEvent', 'TalkPartyEvent']
    sql_list = []
    for i in range(len(table_list)):
        sql_list.append(pre_sql_events.format(table=table_list[i], type=i))
    sql_all_events = " UNION ALL ".join(sql_list) + " ORDER BY jp_start, as_start"

    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_all_events)
        events = cursor.fetchall()
    connection.close()
    return events


def main():
    parser = argparse.ArgumentParser(description='Arguments for move_events.py')
    parser.add_argument('--real', action="store_true", default=False, help='real run')    
    args = parser.parse_args()

    events = get_all_events()

    connection = connect()
    with connection.cursor() as cursor:
        sql_ins_events = """INSERT INTO `Event`
                            (`jp_name`, `as_name`, `jp_start`, `jp_over`,
                            `as_start`, `as_over`, `event_type`, `fake_id`, 
                            `event_subtype`, comment) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        if not args.real:
            cursor = DryCursor(cursor)

        for e in events:
            cursor.execute(sql_ins_events, (e['jp_name'], e['as_name'], 
                e['jp_start'], e['jp_over'], e['as_start'], e['as_over'], 
                e['event_type'], e['id'], e['event_subtype'], e['comment']))
            connection.commit()
    connection.close()

if __name__ == '__main__':
    main()