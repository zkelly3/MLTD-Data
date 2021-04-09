from datetime import timezone, timedelta
from json import loads
import os.path

from flask import Flask
from flask import render_template, url_for, abort
from flask.json import dumps

from config import connect

class NotFoundError(Exception):
    pass

app = Flask(__name__)
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

idol_types = ['All', 'Princess', 'Fairy', 'Angel', 'Guest']
aquire_types = [{'jp': 'プラチナガシャ', 'as': '白金轉蛋'},
    {'jp': 'PSTイベント', 'as': 'PST活動'},
    {'jp': 'ミリコレ', 'as': '百萬收藏'},
    {'jp': '初始', 'as': '初始'},
    {'jp': '周年イベント', 'as': '週年活動'},
    {'jp': '覚醒', 'as': '覺醒'},
    {'jp': 'その他', 'as': '其他'}] # Guest 劇情之類, 其他活動
gasha_types = [{'jp': 'タイプ限定', 'as': '屬性限定'},
    {'jp': '一般', 'as': '一般'},
    {'jp': '期間限定', 'as': '期間限定'},
    {'jp': 'フェス限定', 'as': 'FES限定'},
    {'jp': '限定復刻', 'as': '限定復刻'},
    {'jp': '特殊', 'as': '特殊'}]
event_types = [{'jp': 'PSTイベント', 'as': 'PST活動'},
    {'jp': 'ミリコレ', 'as': '百萬收藏'},
    {'jp': '周年イベント', 'as': '週年活動'},
    {'jp': 'MILLION LIVE WORKING☆', 'as': 'MILLION LIVE WORKING☆'},
    {'jp': 'THEATER SHOW TIME☆', 'as': 'THEATER SHOW TIME☆'},
    {'jp': 'その他', 'as': '其他'},
    {'jp': 'THEATER TALK PARTY☆', 'as': 'THEATER TALK PARTY☆'}]
pst_types = [{'jp': 'シアター', 'as': '劇場'},
    {'jp': 'ツアー', 'as': '巡演'},
    {'jp': 'ツインステージ', 'as': 'ツインステージ'},
    {'jp': 'チューン', 'as': 'チューン'},
    {'jp': 'テール', 'as': 'テール'}
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

        db_res = cursor.fetchall()
        res = []
        for dbr in db_res:
            res.append({'id': dbr['id'],
                'url': image_path('images/idol_icons', str(dbr['id']) + '.png'),
                'jp_name': dbr['jp_name'],
                'as_name': dbr['as_name'],
                'i_type': idol_types[dbr['type']],
                'age': dbr['age'],
                'height': dbr['height'],
                'weight': dbr['weight']})
        connection.close()
        return res

def get_idol_info(idol_id):
    sql_info = "SELECT * FROM `Idol` WHERE id = %s"
    sql_cards = """SELECT id, jp_name, as_name, rare, jp_time, as_time FROM `Card` WHERE (IID = %s)
                   ORDER BY jp_time, as_time, card_id"""
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_info, (idol_id))
        info = cursor.fetchall()
        if not info:
            raise NotFoundError
        info = info[0]
        info['img_url'] = image_path('images/idol_icons', str(info['id']) + '.png')
        info['i_type'] = idol_types[info['type']]
        cursor.execute(sql_cards, (info['id']))
        cards = cursor.fetchall()
    connection.close()

    for card in cards:
        card['img_url'] = image_path('images/card_icons', str(card['id']) + '.png')
        if card['jp_time']:
            card['jp_time'] = card['jp_time'].strftime('%Y-%m-%d')
        if card['as_time']:
            card['as_time'] = card['as_time'].strftime('%Y-%m-%d')
        card['url'] = '/card/' + str(card['id'])
        card['rare'] = rarity[card['rare']]
    return info, cards

def get_card_aquire_local(card, card_id, aquire_id, local, cursor):
    sql_gasha = """SELECT Gasha.id AS id, Gasha.{name} AS name,
                   Gasha.{start} AS start, Gasha.{over} AS over, Gasha.type AS gasha_type
                   FROM `GashaToCard` INNER JOIN `Gasha` ON GashaToCard.GID = Gasha.id
                   WHERE (GashaToCard.CID = %s AND Gasha.{start} IS NOT NULL)
                   ORDER BY Gasha.{start}""".format(**local)
    sql_not_up = """SELECT id, {name} AS name, {start} AS start, {over} AS over, type AS gasha_type
                    FROM `Gasha` WHERE ({start} = %s AND NOT type = 5)""".format(**local)
    pre_sql_event = """SELECT `{event}`.id AS id, {event}.{name} AS name, {event}.{start} AS start, {event}.{over} AS over{other_params}
                   FROM `{event_to_card}` INNER JOIN `{event}` ON {event_to_card}.EID = {event}.id
                   WHERE ({event_to_card}.CID = %s AND {event}.{start} IS NOT NULL)
                   ORDER BY {event}.{start}"""
    
    card['aquire'] = {'type': aquire_types[aquire_id][local['ver']]} if aquire_id is not None else None
    
    guest_commu = {'jp': 'ゲストコミュ', 'as':'ゲストコミュ'}
    if card_id == 1455: # 世界に冠たる絶対女王　玲音
        card['from'] = 'Else'
        card['aquire']['title'] = guest_commu[local['ver']]
        return
    
    tz_info = timezone(timedelta(hours=local['ver_time']))
    if aquire_id == 0:
        card['from'] = 'Gasha'
        cursor.execute(sql_gasha, (card_id))
        gashas = cursor.fetchall()
        if not gashas:
            cursor.execute(sql_not_up, (card['time']))
            gashas = cursor.fetchall()
        for gasha in gashas:
            gasha['start'] = gasha['start'].replace(tzinfo=tz_info).timestamp()
            gasha['over'] = gasha['over'].replace(tzinfo=tz_info).timestamp()
            gasha['gasha_type'] = gasha_types[gasha['gasha_type']][local['ver']]
        card['gashas'] = gashas
        card['aquire']['title'] = gashas[0]['name'] if gashas else None
    elif aquire_id in [3, 5]:
        card['from'] = 'Else'
        card['aquire']['title'] = '--'
    else:
        card['from'] = 'Event'
        e_local = loads(dumps(local))
        if aquire_id == 1:
            e_local['event'] = 'PSTEvent'
            e_local['event_to_card'] = 'PSTEventToCard'
            e_local['other_params'] = ', PSTEvent.type AS event_type'
        elif aquire_id == 2:
            e_local['event'] = 'CollectEvent'
            e_local['event_to_card'] = 'CollectEventToCard'
            e_local['other_params'] = ''
        elif aquire_id == 4:
            e_local['event'] = 'Anniversary'
            e_local['event_to_card'] = 'AnniversaryToCard'
            e_local['other_params'] = ''
        else:
            e_local['event'] = 'OtherEvent'
            e_local['event_to_card'] = 'OtherEventToCard'
            e_local['other_params'] = ''
        
        sql_event = pre_sql_event.format(**e_local)
        cursor.execute(sql_event, (card_id))
        event = cursor.fetchall()
        event = event[0] if event else None
        card['aquire']['title'] = event['name'] if event else None
        card['event'] = event
        if card['event']:
            card['event']['start'] = card['event']['start'].replace(tzinfo=tz_info).timestamp()
            card['event']['over'] = card['event']['over'].replace(tzinfo=tz_info).timestamp()
            card['event']['event_type'] = pst_types[event['event_type']][local['ver']] if aquire_id == 1 else aquire_types[aquire_id][local['ver']]
        

def get_card_l_skill_local(card, card_id, rare_id, local, cursor):
    sql_l_skill = """SELECT id, {name} AS name, {description} AS description, ssr, sr, r
                FROM `LeaderSkill` WHERE (id = %s)""".format(**local)
    
    l_skill_id = card.pop('leader_skill', None)
    if rare_id >= 2 and l_skill_id is not None:
        cursor.execute(sql_l_skill, (l_skill_id))
        l_skill = cursor.fetchall()
        if l_skill:
            l_skill = l_skill[0]
            card['leader_skill'] = {'name': l_skill['name']}

            if rare_id >= 6:
                ls_val = loads(l_skill['ssr']) if l_skill['ssr'] is not None else None
            elif rare_id >= 4:
                ls_val = loads(l_skill['sr']) if l_skill['sr'] is not None else None
            elif rare_id >= 2:
                ls_val = loads(l_skill['sr']) if l_skill['r'] is not None else None
            else:
                ls_val = None

            card['leader_skill']['description'] = l_skill['description'].format(**ls_val) if l_skill['description'] is not None and ls_val is not None else ''

def get_card_skill_local(card, card_id, rare_id, local, cursor):
    sql_skill = """SELECT SkillType.id AS id, SkillType.{name} AS name,
                   SkillSubType.{description} AS description FROM `SkillSubType`
                   INNER JOIN `SkillType` ON SkillSubType.SID = SkillType.id
                   WHERE (SkillSubType.id = %s)""".format(**local)
    
    skill_type_id = card.pop('skill_type', None)
    if rare_id >= 2 and skill_type_id is not None:
        cursor.execute(sql_skill, (skill_type_id))
        skill = cursor.fetchall()
        if skill:
            skill = skill[0]
            card['skill'] = {'name': card.pop('skill_name', None), 'type': {'id': skill['id'], 'name': skill['name']}}

            skill_val = card.pop('skill_val', None)
            skill_val = loads(skill_val) if skill_val is not None else None
            card['skill']['description'] = skill['description'].format(**skill_val) if skill['description'] is not None and skill_val is not None else ''

def get_card_info_local(card_id, local):
    # sql_e_col = ""
    # ssql_e_pst = ""
    # ssql_e_ann = ""
    # ssql_e_oth = ""

    sql_card = """SELECT id, {name} AS name, IID, rare, {time} AS time, aquire, gasha_type, in_gasha,
                  {master_rank} AS master_rank, visual_max, vocal_max, dance_max,
                  visual_bonus, vocal_bonus, dance_bonus, leader_skill, 
                  skill_type, {skill_name} AS skill_name, skill_val,
                  {flavor} AS flavor, awaken
                  FROM `Card` WHERE (id = %s)""".format(**local)
    sql_idol = "SELECT {name} AS name, color FROM `Idol` WHERE (id = %s)".format(**local)
    sql_awaken = "SELECT id, {name} AS name FROM `Card` WHERE (id = %s)".format(**local)
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_card, (card_id))
        card = cursor.fetchall()
        if not card:
            raise NotFoundError

        card = card[0]
        card['is_jp'] = local['ver'] == 'jp'
        
        # 這張卡在這一版不存在或還沒實裝
        if card['time'] is None:
            return None

        # 所屬偶像
        idol_id = card.pop('IID', None)
        if idol_id is not None:
            cursor.execute(sql_idol, (idol_id))
            idol = cursor.fetchall()
            if idol:
                idol = idol[0]
                card['idol'] = {'url': '/idol/%d' % idol_id, 'name': idol['name'], 'color': idol['color']}

        # 稀有度
        rare_id = card['rare']
        card['rare'] = rarity[rare_id]

        # 取得方式
        aquire_id = card.pop('aquire', None)
        get_card_aquire_local(card, card_id, aquire_id, local, cursor)

        # 是否覺醒
        card['is_awaken'] = aquire_id == 5

        # 覺醒前 / 後
        awaken_id = card.pop('awaken', None)
        card['awaken'] = {} if awaken_id is not None else None
        if awaken_id is not None:
            cursor.execute(sql_awaken, (awaken_id))
            awaken = cursor.fetchall()
            if awaken:
                awaken = awaken[0]
                card['awaken']['id'] = awaken['id']
                card['awaken']['name'] = awaken['name']
                card['awaken']['img_url'] = image_path('images/card_icons', '%d.png' % awaken['id'])
                card['awaken']['url'] = '/card/%d' % awaken['id']

        # Center 效果
        get_card_l_skill_local(card, card_id, rare_id, local, cursor)

        # 技能
        get_card_skill_local(card, card_id, rare_id, local, cursor)
        
        # 數值 Bonus
        card['visual_bonus'] = loads(card['visual_bonus']) if card['visual_bonus'] is not None else None
        card['vocal_bonus'] = loads(card['vocal_bonus']) if card['vocal_bonus'] is not None else None
        card['dance_bonus'] = loads(card['dance_bonus']) if card['dance_bonus'] is not None else None
        
        tz_info = timezone(timedelta(hours=local['ver_time']))
        card['time'] = card['time'].replace(tzinfo=tz_info).timestamp() if card['time'] is not None else None
        card['img_url'] = image_path('images/card_images', str(card['id']) + '.png')
    connection.close()
    return card

def get_card_info(card_id):
    jp_local = {'name': 'jp_name',
        'time': 'jp_time',
        'master_rank': 'jp_master_rank',
        'skill_name': 'jp_skill_name',
        'flavor': 'jp_flavor',
        'start': 'jp_start',
        'over': 'jp_over',
        'description': 'jp_description',
        'ver': 'jp',
        'ver_time': 9
    }
    as_local = {'name': 'as_name',
        'time': 'as_time',
        'master_rank': 'as_master_rank',
        'skill_name': 'as_skill_name',
        'flavor': 'as_flavor',
        'start': 'as_start',
        'over': 'as_over',
        'description': 'as_description',
        'ver': 'as',
        'ver_time': 8
    }

    card = []
    card.append(get_card_info_local(card_id, jp_local))
    card.append(get_card_info_local(card_id, as_local))
    return card


@app.route("/")
def home_page():
    idols = get_idols()
    return render_template('mltd.html', idols=dumps(idols))

@app.route("/idol/<int:idol_id>")
def idol_page(idol_id):
    try:
        info, cards = get_idol_info(idol_id)
    except NotFoundError:
        abort(404)
    return render_template('idol.html', title=info['i_type'] + ' ' + info['jp_name'], info=dumps(info, ensure_ascii=False), cards=dumps(cards, ensure_ascii=False))

@app.route("/card/<int:card_id>")
def card_page(card_id):
    try:
        card = get_card_info(card_id)
    except NotFoundError:
        abort(404)

    if card[0] is not None:
        page_title = card[0]['rare'] + ' ' + card[0]['name']
    else:
        page_title = card[1]['rare'] + ' ' + card[1]['name']
    return render_template('card.html', title=page_title, card=dumps(card, ensure_ascii=False))

@app.errorhandler(404)
def page_not_found(unused_error):
    return render_template('page_not_found.html'), 404


#app.run(host="0.0.0.0", port=5000)
