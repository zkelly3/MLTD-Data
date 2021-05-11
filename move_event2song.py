import argparse
from config import connect
from dry_cursor import DryCursor


def get_event2song_rows():
    sql_e2s = """SELECT `EID`, `SID`, `comment` FROM `PSTEventToSong`"""

    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_e2s)
        rows = cursor.fetchall()
    connection.close()
    return rows


def main():
    parser = argparse.ArgumentParser(description='Arguments for move_event2card.py')
    parser.add_argument('--real', action="store_true", default=False, help='real run')    
    args = parser.parse_args()

    rows = get_event2song_rows()

    errors = []
    connection = connect()
    with connection.cursor() as cursor:
        sql_get_event_id = """SELECT id FROM `Event` WHERE (event_type = %s AND fake_id = %s)"""
        sql_ins_e2s = """INSERT INTO `EventToSong`
                            (`EID`, `SID`, `comment`) VALUES(%s, %s, %s)"""

        for r in rows:
            cursor.execute(sql_get_event_id, (0, r['EID']))
            event_id = cursor.fetchall()
            if not event_id:
                errors.append(str(0) + ' ' + str(r['EID']) + ' Not Found')
                continue
            event_id = event_id[0]['id']
            r['id'] = event_id
        if not args.real:
            cursor = DryCursor(cursor)
        for r in rows:
            cursor.execute(sql_ins_e2s, (r['id'], r['SID'], r['comment']))
            connection.commit()
    connection.close()
    for err in errors:
        print(err)

if __name__ == '__main__':
    main()