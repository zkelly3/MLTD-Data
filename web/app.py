from flask import Flask
from flask import render_template, request, url_for, abort
from flask.json import dumps
import pymysql.cursors
from datetime import datetime
import os.path

app = Flask(__name__)
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

idol_types = ['All', 'Princess', 'Fairy', 'Angel', 'Guest']
aquire_types = [{'jp': 'プラチナガシャ', 'cn': '白金轉蛋'}, 
    {'jp': 'PSTイベント', 'cn': 'PST活動'}, 
    {'jp': 'ミリコレ', 'cn': '百萬收藏'}, 
    {'jp': '初始', 'cn': '初始'},
    {'jp': '周年イベント', 'cn': '週年活動'},
    {'jp': '覚醒', 'cn': '覺醒'},
    {'jp': 'その他', 'cn': '其他'}] # Guest 劇情之類, 其他活動
event_types = [{'jp': 'PSTイベント', 'cn': 'PST活動'},
    {'jp': 'ミリコレ', 'cn': '百萬收藏'},
    {'jp': '周年イベント', 'cn': '週年活動'},
    {'jp': 'MILLION LIVE WORKING☆', 'cn': 'MILLION LIVE WORKING☆'},
    {'jp': 'THEATER SHOW TIME☆', 'cn': 'THEATER SHOW TIME☆'},
    {'jp': 'その他', 'cn': '其他'}]
pst_types = [{'jp': 'シアター', 'cn': '劇場'},
    {'jp': 'ツアー', 'cn': '巡演'},
    {'jp': 'ツインステージ', 'cn': 'ツインステージ (海外版尚未上)'},
    {'jp': 'チューン', 'cn': 'チューン (海外版尚未上)'},
    {'jp': 'テール', 'cn': 'テール (海外版尚未上)'}
]

rarity = ['N', 'N＋', 'R', 'R＋', 'SR', 'SR＋', 'SSR', 'SSR＋']

def connect():
    return pymysql.connect(host='localhost', user='zkelly3', password='zkelly3@pibb', db='mltd', charset = 'utf8', cursorclass=pymysql.cursors.DictCursor)

def get_idols():
    connection = connect()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM Idol"
        cursor.execute(sql)

        dbres = cursor.fetchall()
        res = []
        for dbr in dbres:
            img_dir = 'images/idol_icons'
            img_name = str(dbr['id']) + '.png'
            img_path = os.path.join(img_dir, img_name)
            url = url_for('static', filename=img_path)
            res.append({'id': dbr['id'],
                'url': url,
                'name': dbr['name'],
                'itype': idol_types[dbr['type']],
                'age': dbr['age'],
                'height': dbr['height'],
                'weight': dbr['weight']})
        connection.close()
        return res

def get_idol_info(id):
    sql1 = "SELECT * FROM Idol WHERE id = %s"
    sql2 = "SELECT id, name, cnname, rare, time, astime FROM Card WHERE (IID = %s) ORDER BY cardid"
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql1, (id));
        info = cursor.fetchall()
        if not info:
            raise KeyError
        else:
            info = info[0]
            img_dir = 'images/idol_icons'
            img_name = str(info['id']) + '.png'
            img_path = os.path.join(img_dir, img_name)
            info['url'] = url_for('static', filename=img_path)
            info['itype'] = idol_types[info['type']]
            cursor.execute(sql2, (info['id']))
            cards = cursor.fetchall()
    connection.close()
    
    for card in cards:
        img_dir = 'images/card_icons'
        img_name = str(card['id']) + '.png'
        img_path = os.path.join(img_dir, img_name)
        card['url'] = url_for('static', filename=img_path)
        if card['time']:
            card['time'] = card['time'].strftime('%Y-%m-%d')
        if card['astime']:
            card['astime'] = card['astime'].strftime('%Y-%m-%d')
        card['rare'] = rarity[card['rare']]
    return info, cards

@app.route("/")
def home_page():
    idols = get_idols()
    return render_template('mltd.html', idols=dumps(idols))

@app.route("/idol/<int:id>")
def idol_page(id):
    try:
        info, cards = get_idol_info(id)
    except KeyError as e:
        abort(404)
    return render_template('idol.html', title=info['itype'] + ' ' + info['name'], info=dumps(info), cards=dumps(cards))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


#app.run(host="0.0.0.0", port=5000)
