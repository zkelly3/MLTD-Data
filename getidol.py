from config import *
import csv

def main():
    data = []
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT name, cnname, type FROM Idol"
        cursor.execute(sql)
        results = cursor.fetchall()
        print('name, cnname, type')
        for res in results:
            #print(res)
            print(res['name'], res['cnname'], res['type'])
    connection.close()

if __name__ == '__main__':
    main()
