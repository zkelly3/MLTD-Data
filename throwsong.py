from config import *
import csv

def main():
    data = []
    with open('mltdsong.csv', newline='') as f:
        rows = csv.DictReader(f)
        for row in rows:
            data.append({'name': row['曲名'], 'ingame': row['實裝後曲種']})
    connection = connect()
    for d in data:
        with connection.cursor() as cursor:
            print(d['name'], d['ingame'])
            sql = "INSERT INTO `Song`(`name`, `ingame`, `asingame`) VALUES(%s, %s, %s)"
            if d['ingame'] == '':
                cursor.execute(sql, (d['name'], 0, 0))
            else:
                cursor.execute(sql, (d['name'], 1, 0))
        connection.commit()

if __name__ == '__main__':
    main()
