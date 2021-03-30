from config import *
import csv

def main():
    data = []
    with open('mltdidol.csv', newline='') as f:
        rows = csv.DictReader(f)
        for row in rows:
            data.append({'name': row['名稱'], 'itype': row['陣營']})
    connection = connect()
    with connection.cursor() as cursor:
        print('yes')
        for d in data:
            print(d['name'], d['itype'])
            sql = "INSERT INTO `Idol`(`name`, `type`) VALUES(%s, %s)"
            cursor.execute(sql, (d['name'], d['itype']))
    connection.commit()

if __name__ == '__main__':
    main()
