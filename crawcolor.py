import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from config import connect

def bs4_data(url, *args, **kwargs):
    rq = requests.get(url)
    rq.encoding = 'utf-8'
    soup = BeautifulSoup(rq.text,"html.parser")
    res = soup.find_all(*args, **kwargs)
    
    return res

def consume(s, prefix):
    if not s.startswith(prefix):
        return False, None
    else:
        return True, s[len(prefix):].strip()

def main():
    get_idols = "SELECT id, as_name FROM `Idol` WHERE (color IS NULL AND NOT type = 4)"
    set_color = "UPDATE `Idol` SET color = %s WHERE (id = %s)"
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(get_idols)
        idols = cursor.fetchall()
        for idol in idols:
            name = idol['as_name']
            url = 'https://zh.moegirl.org.cn/' + name
            span = bs4_data(url, string=re.compile('.*印象色是.*'))
            if span:
                color = span[0].nextSibling.find('span')["style"].split(':')[1][:-1]
                print(name, color)
                cursor.execute(set_color, (color, idol['id']))
            connection.commit()
    connection.close()

if __name__ == '__main__':
    main()