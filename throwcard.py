from config import *
import csv

def main():
    data = []
    with open('mltd_all.csv', newline='') as f:
        rows = csv.DictReader(f)
        for row in rows:
            data.append(row)
    connection = connect()

    for d in data:
        sql1 = "SELECT id FROM `Aquire` WHERE (name = %s)"
        sql2 = "SELECT id FROM `LeaderSkill` WHERE (name = %s)"
        sql3 = "SELECT id FROM `SkillType` WHERE (name = %s)"
        sql4 = "INSERT INTO `Card`(`name`, `cnname`, `rare`, `time`, `astime`, `aquire`, `limit`, `inpool`, `leaderskill`, `skilltype`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        for key in d:
            if d[key] == '':
                d[key] = None

        with connection.cursor() as cursor:
            aquire = 0
            if d['aquire']:
                cursor.execute(sql1, (d['aquire']))
                aquire = cursor.fetchall()[0]['id']

            leader_skill = 0
            if d['leaderskill']:
                cursor.execute(sql2, (d['leaderskill']))
                leader_skill = cursor.fetchall()[0]['id']

            skill_type = 0
            if d['skilltype']:
                cursor.execute(sql3, (d['skilltype']))
                skill_type = cursor.fetchall()[0]['id']


            if d['name']:
                name = d['name']
            else:
                name = d['cnname']
            print(name, aquire, leader_skill, skill_type)

            if aquire == 0:
                aquire = None
            if leader_skill == 0:
                leader_skill = None
            if skill_type == 0:
                skill_type = None

            cursor.execute(sql4, (d['name'], d['cnname'], d['rare'], d['time'], d['astime'], aquire, d['limit'], d['inpool'], leader_skill, skill_type))

        connection.commit()

    connection.close()


if __name__ == '__main__':
    main()
