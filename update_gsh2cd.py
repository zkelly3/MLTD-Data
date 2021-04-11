from config import *


def main():
    data = []
    with open('gsh2cd.txt') as f:
        line = f.readline()
        while line:
            data.append(line.strip().split(' '))
            line = f.readline()

    connection = connect()
    upd_gsh2cd = 'INSERT INTO `GashaToCard`(`GID`, `CID`) VALUES(%s, %s)'
    with connection.cursor() as cursor:
        for d in data:
            cursor.execute(upd_gsh2cd, (int(d[0]), int(d[1])))
            connection.commit()
    connection.close()


if __name__ == '__main__':
    main()