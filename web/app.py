from flask import Flask
from flask import render_template, request, url_for, abort
from flask.json import dumps
from json import loads
from config import *
from datetime import datetime, timezone, timedelta
import os.path

class NotFoundError(Exception):
    pass

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
    {'jp': 'ツインステージ', 'cn': 'ツインステージ'},
    {'jp': 'チューン', 'cn': 'チューン'},
    {'jp': 'テール', 'cn': 'テール'}
]

rarity = ['N', 'N＋', 'R', 'R＋', 'SR', 'SR＋', 'SSR', 'SSR＋']

def image_path(img_dir, img_name):
    img_path = os.path.join(img_dir, img_name)
    return url_for('static', filename=img_path)

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
    sql_info = "SELECT * FROM `Idol` WHERE id = %s"
    sql_cards = "SELECT id, name, cnname, rare, time, astime FROM `Card` WHERE (IID = %s) ORDER BY cardid"
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_info, (id));
        info = cursor.fetchall()
        if not info:
            raise NotFoundError
        else:
            info = info[0]
            img_dir = 'images/idol_icons'
            img_name = str(info['id']) + '.png'
            img_path = os.path.join(img_dir, img_name)
            info['url'] = url_for('static', filename=img_path)
            info['itype'] = idol_types[info['type']]
            cursor.execute(sql_cards, (info['id']))
            cards = cursor.fetchall()
    connection.close()
    
    for card in cards:
        img_dir = 'images/card_icons'
        img_name = str(card['id']) + '.png'
        img_path = os.path.join(img_dir, img_name)
        card['img_url'] = url_for('static', filename=img_path)
        if card['time']:
            card['time'] = card['time'].strftime('%Y-%m-%d')
        if card['astime']:
            card['astime'] = card['astime'].strftime('%Y-%m-%d')
        card['url'] = '/card/' + str(card['id'])
        card['rare'] = rarity[card['rare']]
    return info, cards

def get_card_info(id):
    sql_card = "SELECT * FROM `Card` WHERE (id = %s)"
    sql_idol = "SELECT name, cnname FROM `Idol` WHERE (id = %s)"
    sql_awaken = "SELECT id, name, cnname FROM `Card` WHERE (id = %s)"
    sql_ls = "SELECT * FROM `LeaderSkill` WHERE (id = %s)"
    sql_skill = """SELECT SkillType.id AS id, SkillType.name AS name, SkillType.cnname AS cnname,
    SkillSubType.description AS description, SkillSubType.cndescription AS cndescription
    FROM `SkillSubType` INNER JOIN `SkillType` ON SkillSubType.SID = SkillType.id
    WHERE (SkillSubType.id = %s)"""
    sql_gasha = """SELECT GashaToCard.comment AS g2cComment, 
    Gasha.id AS gid, Gasha.name AS gashaName, Gasha.cnname AS gashaCNName, Gasha.start AS gashaStart, Gasha.over AS gashaOver,
    Gasha.asstart AS gashaASStart, Gasha.asover AS gashaASOver, Gasha.type AS gashaType, Gasha.comment AS gashaComment
    FROM `GashaToCard` INNER JOIN `Gasha` ON GashaToCard.GID = Gasha.id
    WHERE (GashaToCard.CID = %s) ORDER BY Gasha.start, Gasha.asstart"""
    sql_notup = "SELECT * FROM `Gasha` WHERE (start = %s AND NOT type = 5)"
    sql_notupas = "SELECT * FROM `Gasha` WHERE (asstart = %s AND NOT type = 5)"
    sql_e_col = ""
    sql_e_pst = ""
    sql_e_ann = ""
    sql_e_oth = ""
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_card, (id));
        card = cursor.fetchall()
        if not card:
            raise NotFoundError
        else:
            card = card[0]
            
            idol_id = card.pop('IID', None)
            if idol_id is not None:
                cursor.execute(sql_idol, (idol_id))
                idol = cursor.fetchall()
                if idol:
                    card['idol'] = idol[0]
                    card['idol']['url'] = '/idol/' + str(idol_id)
            
            rare_id = card['rare']
            card['rare'] = rarity[rare_id]
            
            aquire_id = card.pop('aquire', None)
            card['aquire'] = {'type': aquire_types[aquire_id]} if aquire_id is not None else None
            if aquire_id == 0:
                cursor.execute(sql_gasha, (id))
                gashas = cursor.fetchall()
                if not gashas:
                    if card['name'] is not None:
                        cursor.execute(sql_notup, (card['time']))
                        card['gasha'] = cursor.fetchall()
                    else:
                        cursor.execute(sql_notupas, (card['astime']))
                        card['gasha'] = cursor.fetchall()
                else:
                    card['gasha'] = gashas
                
                card['aquire']['name'] = card['gasha'][0]['gashaName'] if card['gasha'] else None
                card['aquire']['cnname'] = card['gasha'][0]['gashaCNName'] if card['gasha'] else None
            
                for gasha in card['gasha']:
                    gasha['gashaStart'] = gasha['gashaStart'].replace(tzinfo=timezone(timedelta(hours=9))).timestamp() if gasha['gashaStart'] is not None else None
                    gasha['gashaOver'] = gasha['gashaOver'].replace(tzinfo=timezone(timedelta(hours=9))).timestamp() if gasha['gashaOver'] is not None else None
                    gasha['gashaASStart'] = gasha['gashaASStart'].replace(tzinfo=timezone(timedelta(hours=8))).timestamp() if gasha['gashaASStart'] is not None else None
                    gasha['gashaASOver'] = gasha['gashaASOver'].replace(tzinfo=timezone(timedelta(hours=8))).timestamp() if gasha['gashaASOver'] is not None else None
            elif aquire_id == 5:
                card['aquire']['name'] = '/'
                card['aquire']['cnname'] = '/'
            
            card['is_awaken'] = True if aquire_id == 5 else False
            awaken_id = card.pop('awaken', None)
            card['awaken'] = {} if awaken_id is not None else None
            if awaken_id is not None:
                cursor.execute(sql_awaken, (awaken_id))
                awaken = cursor.fetchall()
                if awaken:
                    awaken = awaken[0]
                    card['awaken']['id'] = awaken['id']
                    card['awaken']['name'] = awaken['name']
                    card['awaken']['cnname'] = awaken['cnname']
                    card['awaken']['img_url'] = image_path('images/card_icons', str(awaken['id']) + '.png')
                    card['awaken']['url'] = '/card/' + str(awaken['id'])
                
            if rare_id >= 2 and card['leaderskill'] is not None:
                cursor.execute(sql_ls, (card['leaderskill']))
                ls = cursor.fetchall()
                if ls:
                    ls = ls[0]
                    card['leaderskill'] = {}
                    card['leaderskill']['name'] = ls['name']
                    card['leaderskill']['cnname'] = ls['cnname']
                    if ls['description'] is not None:
                        if rare_id >= 6:
                            ls_val = loads(ls['ssr']) if ls['ssr'] is not None else None
                        elif rare_id >= 4:
                            ls_val = loads(ls['sr']) if ls['sr'] is not None else None
                        elif rare_id >= 2:
                            ls_val = loads(ls['sr']) if ls['r'] is not None else None
                        else:
                            ls_val = None
                        
                        if ls_val is not None:
                            card['leaderskill']['description'] = ls['description'].format(**ls_val)
                        else:
                            card['leaderskill']['description'] = ''
                else:
                    card['leaderskill'] = None
            
            skilltype_id = card.pop('skilltype', None)
            if rare_id >= 2 and skilltype_id is not None:
                cursor.execute(sql_skill, (skilltype_id))
                skill = cursor.fetchall()
                if skill:
                    skill = skill[0]
                    card['skill'] = {}
                    card['skill']['name'] = card.pop('skillname', None)
                    card['skill']['type'] = {}
                    card['skill']['type']['id'] = skill['id']
                    card['skill']['type']['name'] = skill['name']
                    card['skill']['type']['cnname'] = skill['cnname']
                    skill_val = card.pop('skillval', None)
                    skill_val = loads(skill_val) if skill_val is not None else None
                    card['skill']['description'] = skill['description'].format(**skill_val) if skill['description'] is not None and skill_val is not None else ''
                    card['skill']['cndescription'] = skill['cndescription'].format(**skill_val) if skill['cndescription'] is not None and skill_val is not None else ''
            
            card['time'] = card['time'].replace(tzinfo=timezone(timedelta(hours=9))).timestamp() if card['time'] is not None else None
            card['astime'] = card['astime'].replace(tzinfo=timezone(timedelta(hours=8))).timestamp() if card['astime'] is not None else None
            
            card['url'] = image_path('images/card_images', str(card['id']) + '.png')
    connection.close()
    return card
    
    
@app.route("/")
def home_page():
    idols = get_idols()
    return render_template('mltd.html', idols=dumps(idols))

@app.route("/idol/<int:id>")
def idol_page(id):
    try:
        info, cards = get_idol_info(id)
    except NotFoundError as e:
        abort(404)
    return render_template('idol.html', title=info['itype'] + ' ' + info['name'], info=dumps(info, ensure_ascii=False), cards=dumps(cards, ensure_ascii=False))

@app.route("/card/<int:id>")
def card_page(id):
    try:
        card = get_card_info(id)
    except NotFoundError as e:
        abort(404)
    return render_template('card.html', title=card['rare'] + ' ' + card['name'], card=dumps(card, ensure_ascii=False))
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


#app.run(host="0.0.0.0", port=5000)
