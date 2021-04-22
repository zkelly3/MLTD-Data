from datetime import timezone, timedelta
from json import loads
import os.path

from flask import Flask
from flask import render_template, url_for, redirect, abort
from flask.json import dumps

from config import connect, jp_local, as_local

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
gasha_types = [{'jp': 'タイプ限定', 'as': '屬性限定', 'abbr': 'TYP'},
    {'jp': '一般', 'as': '一般', 'abbr': 'NML'},
    {'jp': '期間限定', 'as': '期間限定', 'abbr': 'LMT'},
    {'jp': 'フェス限定', 'as': 'FES限定', 'abbr': 'FES'},
    {'jp': '限定復刻', 'as': '限定復刻', 'abbr': 'RET'},
    {'jp': '特殊', 'as': '特殊', 'abbr': 'SPC'}]
event_types = [{'jp': 'PSTイベント', 'as': 'PST活動', 
     'abbr': 'PST', 'table': 'PSTEvent', 'to_card_table': 'PSTEventToCard'},
    {'jp': 'ミリコレ', 'as': '百萬收藏', 
     'abbr': 'COL', 'table': 'CollectEvent', 'to_card_table': 'CollectEventToCard'},
    {'jp': '周年イベント', 'as': '週年活動', 
     'abbr': 'ANN', 'table': 'Anniversary', 'to_card_table': 'AnniversaryToCard'},
    {'jp': 'MILLION LIVE WORKING☆', 'as': 'MILLION LIVE WORKING☆', 
     'abbr': 'WRK', 'table': 'WorkingEvent'},
    {'jp': 'THEATER SHOW TIME☆', 'as': 'THEATER SHOW TIME☆', 
     'abbr': 'SHT', 'table': 'ShowTimeEvent'},
    {'jp': 'その他', 'as': '其他', 
     'abbr': 'OTH', 'table': 'OtherEvent', 'to_card_table': 'OtherEventToCard'},
    {'jp': 'THEATER TALK PARTY☆', 'as': 'THEATER TALK PARTY☆', 
     'abbr': 'TKP', 'table': 'TalkPartyEvent'}]
pst_types = [{'jp': 'シアター', 'as': '劇場'},
    {'jp': 'ツアー', 'as': '巡演'},
    {'jp': 'ツインステージ', 'as': 'ツインステージ'},
    {'jp': 'チューン', 'as': 'チューン'},
    {'jp': 'テール', 'as': 'テール'}
]
card_types = [{'jp': '一般', 'as': '一般', 'abbr': 'NML'}, # 初始、常駐、百萬收藏 (N, R, SR, SSR)
{'jp': '期間限定', 'as': '期間限定', 'abbr': 'LMT'}, # 期間限定 (SR, SSR)
{'jp': 'フェス限定', 'as': 'FES限定', 'abbr': 'FES'}, # FES限定 (SR, SSR)
{'jp': 'PSTイベント', 'as': 'PST活動', 'abbr': 'PST'}, # PST活動 (SR)
{'jp': '1周年', 'as': '1週年', 'abbr': '1ST'}, # 1st (SR)
{'jp': '2周年', 'as': '2週年', 'abbr': '2ND'}, # 2nd (SR)
{'jp': '3周年', 'as': '3週年', 'abbr': '3RD'}, # 3rd (SR)
]
l_skill_types = [{'jp': '全アピールアップ', 'as': '全表現值提升', 'val': 0},
{'jp': 'ビジュアルアップ', 'as': '視覺值提升', 'val': 1},
{'jp': 'ボーカルアップ', 'as': '歌唱值提升', 'val': 2},
{'jp': 'ダンスアップ', 'as': '舞蹈值提升', 'val': 3},
{'jp': 'ライフアップ', 'as': '體力提升', 'val': 4},
{'jp': 'スキル発動率アップ', 'as': '技能發動率提升', 'val': 5},
]

rarity = ['N', 'N＋', 'R', 'R＋', 'SR', 'SR＋', 'SSR', 'SSR＋']

def image_path(img_dir, img_name):
    img_path = os.path.join(img_dir, img_name)
    return url_for('static', filename=img_path)

def to_timestamp(target, tz_info):
    return target.replace(tzinfo=tz_info).timestamp() if target is not None else None

def get_idols_info_local(local):
    sql_all_idols = """SELECT id, {name} AS name, type AS idol_type, 
                        CV, age, height, weight FROM Idol""".format(**local)
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_all_idols)
        idols = cursor.fetchall()
        for idol in idols:
            idol['img_url'] = image_path('images/idol_icons', '%d.png' % idol['id'])
            idol['url'] = '/idol/%d' % idol['id']
            idol['idol_type'] = idol_types[idol['idol_type']] if idol['idol_type'] is not None else None
    connection.close()
    
    return idols

def get_idols_info():
    idols = []
    idols.append(get_idols_info_local(jp_local))
    idols.append(get_idols_info_local(as_local))
    
    return idols

def get_events_info_local(local):
    pre_sql_all_events_columns = """SELECT id, {name} AS name,
                                    '{type_id}' AS type_id, '{event_abbr}' AS event_abbr,
                                    {start} AS start, {over} AS over FROM `{event}`
                                    WHERE {start} IS NOT NULL"""
    
    tz_info = timezone(timedelta(hours=local['ver_time']))
    
    sql_list = []
    for i in range(len(event_types)):
        event = event_types[i]
        e_local = loads(dumps(local))
        e_local['event'] = event['table']
        e_local['event_abbr'] = event['abbr']
        e_local['type_id'] = i
        sql_list.append(pre_sql_all_events_columns.format(**e_local))
    
    sql_all_events = " UNION ALL ".join(sql_list) + " ORDER BY start DESC"
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_all_events)
        events = cursor.fetchall()
    connection.close()
    
    for event in events:
        type_id = int(event.pop('type_id', len(event_types)))
        id = int(event.pop('id', 0))
        event['url'] = '/event/%d/%d' % (type_id, id)
        event['start'] = to_timestamp(event['start'], tz_info)
        event['over'] = to_timestamp(event['over'], tz_info)
    
    return events

def get_event_types_local(local):
    types = []
    for event_type in event_types:
        types.append({
            'val': event_type['abbr'],
            'text': event_type[local['ver']],
        })
    return types

def get_events_info():
    events = []
    events.append(get_events_info_local(jp_local))
    events.append(get_events_info_local(as_local))
    
    types = []
    types.append(get_event_types_local(jp_local))
    types.append(get_event_types_local(as_local))
    
    return events, types

def get_gashas_info_local(local):
    sql_all_gashas = """SELECT id, {name} AS name, type AS type_id, 
                        {start} AS start, {over} AS over FROM `Gasha`
                        WHERE {start} IS NOT NULL
                        ORDER BY {start} DESC""".format(**local)
    
    tz_info = timezone(timedelta(hours=local['ver_time']))

    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_all_gashas)
        gashas = cursor.fetchall()
    connection.close()
    
    for gasha in gashas:
        type_id = int(gasha.pop('type_id', len(gasha_types)))
        gasha['gasha_abbr'] = gasha_types[type_id]['abbr']
        gasha['url'] = '/gasha/%d' % gasha['id']
        gasha['start'] = to_timestamp(gasha['start'], tz_info)
        gasha['over'] = to_timestamp(gasha['over'], tz_info)
    
    return gashas

def get_gasha_types_local(local):
    types = []
    for gasha_type in gasha_types:
        types.append({
            'val': gasha_type['abbr'],
            'text': gasha_type[local['ver']],
        })
    return types

def get_gashas_info():
    gashas = []
    gashas.append(get_gashas_info_local(jp_local))
    gashas.append(get_gashas_info_local(as_local))
    
    types = []
    types.append(get_gasha_types_local(jp_local))
    types.append(get_gasha_types_local(as_local))
    
    return gashas, types

def get_cards_info_local(local):
    sql_all_cards = """SELECT `Card`.id AS id, `Card`.{name} AS name, `Idol`.type AS idol_type,
                      `Card`.rare AS rare, `Card`.{time} AS time, `Awaken`.id AS a_id, 
                      `Card`.aquire AS aquire, `Awaken`.aquire AS a_aquire,
                      `Card`.gasha_type AS gasha_type, `Awaken`.gasha_type AS a_gasha_type, 
                      `Card`.in_gasha AS in_gasha, `Awaken`.in_gasha AS a_in_gasha,
                      `SkillSubType`.SID AS skill_type, `LeaderSkill`.type AS l_skill_type
                      FROM `Card` INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                      INNER JOIN `Card` AS `Awaken` ON `Card`.awaken = `Awaken`.id
                      INNER JOIN `SkillSubType` ON `Card`.skill_type = `SkillSubType`.id
                      INNER JOIN `LeaderSkill` ON `Card`.leader_skill = `LeaderSkill`.id
                      WHERE `Card`.{time} IS NOT NULL
                      ORDER BY `Card`.{time} , `Card`.card_id""".format(**local)
    sql_card_anniversary = "SELECT EID FROM `AnniversaryToCard` WHERE (CID = %s)"
    
    tz_info = timezone(timedelta(hours=local['ver_time']))
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_all_cards)
        cards = cursor.fetchall()
    
        for card in cards:
            card['url'] = '/card/%d' % card['id']
            card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
            card['time'] = to_timestamp(card['time'], tz_info)
            card['idol_type'] = idol_types[card['idol_type']]
            card['is_awaken'] = card['rare'] % 2 == 1
            card['rare'] = card['rare'] // 2;
            
            aquire_id = card.pop('aquire', None)
            a_aquire_id = card.pop('a_aquire', None)
            gasha_type = card.pop('gasha_type', None)
            a_gasha_type = card.pop('a_gasha_type', None)
            in_gasha = card.pop('in_gasha', None)
            a_in_gasha = card.pop('a_in_gasha', None)
            
            if (aquire_id == 0 and gasha_type == 2) or (a_aquire_id == 0 and a_gasha_type == 2):
                card['card_type'] = 'FES'
            elif (aquire_id == 0 and gasha_type == 1) or (a_aquire_id == 0 and a_gasha_type == 1):
                card['card_type'] = 'LMT'
            elif aquire_id == 1 or a_aquire_id == 1:
                card['card_type'] = 'PST'
            elif aquire_id == 4:
                ann_types = ['1ST', '2ND', '3RD']
                cursor.execute(sql_card_anniversary, (card['id']))
                anns = cursor.fetchall()
                if anns:
                    card['card_type'] = ann_types[anns[0]['EID']-1]
                else:
                    card['card_type'] = 'NML'
            elif a_aquire_id == 4:
                ann_types = ['1ST', '2ND', '3RD']
                cursor.execute(sql_card_anniversary, (card['a_id']))
                anns = cursor.fetchall()
                if anns:
                    card['card_type'] = ann_types[anns[0]['EID']-1]
                else:
                    card['card_type'] = 'NML'
            else:
                card['card_type'] = 'NML'
    connection.close()    
    
    return cards

def get_card_filters_local(local):
    sql_all_skills = "SELECT id, {name} AS name FROM `SkillType` WHERE {name} IS NOT NULL".format(**local)
    
    filters = {}
    
    # 偶像陣營 (暫時跳過)
    
    # 稀有度
    rarity_labels = {'jp': 'レアリティ', 'as': '稀有度'}
    filters['rarity'] = {
        'type': 'check',
        'label': rarity_labels[local['ver']],
        'enabled': True,
        'options': [{'val': 0, 'text': 'N'}, {'val': 1, 'text': 'R'}, {'val': 2, 'text': 'SR'}, {'val': 3, 'text': 'SSR'}],
        'selected': [],
        'key': 'rare',
    }
    
    # 覺醒
    awaken_labels = {'jp': '覚醒状態', 'as': '覺醒狀態'}
    awaken_options = [{'val': False, 'jp': '覚醒前', 'as': '未覺醒'}, {'val': True, 'jp': '覚醒後', 'as': '已覺醒'}]
    filters['awaken'] = {
        'type': 'check',
        'label': awaken_labels[local['ver']],
        'enabled': True,
        'options': [{'val': option['val'], 'text': option[local['ver']]} for option in awaken_options],
        'selected': [True],
        'key': 'is_awaken',
    }
    
    # 卡片類型
    type_labels = {'jp': 'カテゴリ', 'as': '分類'}
    filters['card_type'] = {
        'type': 'check',
        'label': type_labels[local['ver']],
        'enabled': True,
        'options': [{'val': option['abbr'], 'text': option[local['ver']]} for option in card_types],
        'selected': [],
        'key': 'card_type',
    }
    
    connection = connect()
    with connection.cursor() as cursor:
        # 技能類型
        cursor.execute(sql_all_skills)
        skills = cursor.fetchall()
        skill_label = {'jp': 'スキル', 'as': '技能'}
        filters['skill_type'] = {
            'type': 'check',
            'label': skill_label[local['ver']],
            'enabled': True,
            'options': [{'val': skill['id'], 'text': skill['name']} for skill in skills],
            'selected': [],
            'key': 'skill_type',
        }
        
        # Center效果類型
        l_skill_label = {'jp': 'センター効果', 'as': 'Center效果'}
        filters['l_skill_type'] = {
            'type': 'check',
            'label': l_skill_label[local['ver']],
            'enabled': True,
            'options': [{'val': l_skill_type['val'], 'text': l_skill_type[local['ver']]} for l_skill_type in l_skill_types],
            'selected': [],
            'key': 'l_skill_type',
        }
        
    connection.close()
    
    return filters;

def get_cards_info():
    cards = []
    cards.append(get_cards_info_local(jp_local))
    cards.append(get_cards_info_local(as_local))
    
    filters = []
    filters.append(get_card_filters_local(jp_local))
    filters.append(get_card_filters_local(as_local))
    
    return cards, filters

def get_idol_info_local(idol_id, local):
    sql_idol_info = """SELECT id, {name} AS name, type AS idol_type,
                  age, height, weight, CV, color
                  FROM `Idol` WHERE id = %s""".format(**local)
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_idol_info, (idol_id))
        info = cursor.fetchall()
        if not info:
            raise NotFoundError
    connection.close()
    
    info = info[0]
    info['img_url'] = image_path('images/idol_icons', '%d.png' % info['id'])
    info['idol_type'] = idol_types[info['idol_type']]
    
    return info

def get_idol_cards_local(idol_id, local):
    sql_idol_cards = """SELECT id, {name} AS name, rare, {time} AS time
                        FROM `Card` WHERE (IID = %s AND {time} IS NOT NULL)
                        ORDER BY {time}, card_id""".format(**local)
    
    tz_info = timezone(timedelta(hours=local['ver_time']))
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_idol_cards, (idol_id))
        cards = cursor.fetchall()
    connection.close()
    
    for card in cards:
        card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
        card['url'] = '/card/%d' % card['id']
        card['time'] = to_timestamp(card['time'], tz_info)
    
    return cards

def get_idol_data(idol_id):
    idol = []
    idol.append({'info': get_idol_info_local(idol_id, jp_local),
        'cards': get_idol_cards_local(idol_id, jp_local)})
    idol.append({'info': get_idol_info_local(idol_id, as_local),
        'cards': get_idol_cards_local(idol_id, as_local)})
    
    return idol

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
    
    tz_info = timezone(timedelta(hours=local['ver_time']))
    card['aquire'] = {'type': aquire_types[aquire_id][local['ver']]} if aquire_id is not None else None

    guest_commu = {'jp': 'ゲストコミュ', 'as':'ゲストコミュ'}
    if card_id == 1455: # 世界に冠たる絶対女王　玲音
        card['from'] = 'Else'
        card['aquire']['title'] = guest_commu[local['ver']]
        return

    if aquire_id == 0:
        card['from'] = 'Gasha'
        cursor.execute(sql_gasha, (card_id))
        gashas = cursor.fetchall()
        if not gashas:
            cursor.execute(sql_not_up, (card['time']))
            gashas = cursor.fetchall()
        for gasha in gashas:
            gasha['url'] = '/gasha/%d' % gasha['id']
            gasha['start'] = to_timestamp(gasha['start'], tz_info)
            gasha['over'] = to_timestamp(gasha['over'], tz_info)
            gasha['gasha_type'] = gasha_types[gasha['gasha_type']][local['ver']]
        card['gashas'] = gashas
        card['aquire']['title'] = gashas[0]['name'] if gashas else None
        card['from_url'] = '/gasha/%d' % gashas[0]['id'] if gashas else None
        card['has_from_url'] = card['from_url'] is not None
    elif aquire_id in [3, 5]:
        card['has_from_url'] = False
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
        
        aquire_to_event = {1: 0, 2: 1, 4: 2, 6: 5}
        if card['event']:
            card['has_from_url'] = True
            card['event']['url'] = '/event/%d/%d' % (aquire_to_event[aquire_id], event['id'])
            card['from_url'] = card['event']['url']
            card['event']['start'] = to_timestamp(card['event']['start'], tz_info)
            card['event']['over'] = to_timestamp(card['event']['over'], tz_info)
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
    sql_card = """SELECT id, {name} AS name, IID, rare, {time} AS time, aquire, gasha_type, in_gasha,
                  {master_rank} AS master_rank, visual_max, vocal_max, dance_max,
                  visual_bonus, vocal_bonus, dance_bonus, leader_skill,
                  skill_type, {skill_name} AS skill_name, skill_val,
                  {flavor} AS flavor, awaken
                  FROM `Card` WHERE (id = %s)""".format(**local)
    sql_idol = "SELECT {name} AS name, color, type AS idol_type FROM `Idol` WHERE (id = %s)".format(**local)
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
                card['idol'] = {'url': '/idol/%d' % idol_id, 'name': idol['name'], 
                                'color': idol['color'], 'idol_type': idol_types[idol['idol_type']]}

        # 稀有度
        rare_id = card['rare']

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
        card['time'] = to_timestamp(card['time'], tz_info)
        card['img_url'] = image_path('images/card_images', '%d.png' % card['id'])
        if rare_id >= 6:
            card['big_img_url'] = image_path('images/card_images_bg/', '%d.png' % card['id'])
        
    connection.close()
    return card

def get_card_info(card_id):
    card = []
    card.append(get_card_info_local(card_id, jp_local))
    card.append(get_card_info_local(card_id, as_local))
    return card

def get_event_info_local(event_type, event_id, local):
    pre_sql_event_info = """SELECT id, {name} AS name, 
                            {start} AS start, {over} AS over, comment{other_params}
                            FROM {event} WHERE (id = %s)"""
    pre_sql_event_card_pst = """SELECT `Card`.id AS id, `Card`.{name} AS name,
                                `Card`.rare AS rare, `Idol`.type AS idol_type
                                FROM `PSTEventToCard` INNER JOIN `Card`
                                ON `PSTEventToCard`.CID = `Card`.id
                                INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                                WHERE (`PSTEventToCard`.EID = %s AND `PSTEventToCard`.type = %s)"""
    pre_sql_event_card_col = """SELECT `Card`.id AS id, `Card`.{name} AS name,
                                `Card`.rare AS rare, `Idol`.type AS idol_type
                                FROM `CollectEventToCard` INNER JOIN `Card`
                                ON `CollectEventToCard`.CID = `Card`.id
                                INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                                WHERE (`CollectEventToCard`.EID = %s)
                                ORDER BY `CollectEventToCard`.type"""
    pre_sql_event_card_ann = """SELECT `Card`.id AS id, `Card`.{name} AS name,
                                `Idol`.{name} As idol_name, 
                                `Card`.rare AS rare, `Idol`.type AS idol_type
                                FROM `AnniversaryToCard` INNER JOIN `Card`
                                ON `AnniversaryToCard`.CID = `Card`.id
                                INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                                WHERE (`AnniversaryToCard`.EID = %s AND `AnniversaryToCard`.type = %s)"""
    pre_sql_event_card_oth = """SELECT Card.id AS id, Card.{name} AS name, 
                                `Card`.rare AS rare, `Idol`.type AS idol_type
                                FROM `OtherEventToCard` INNER JOIN `Card`
                                ON `OtherEventToCard`.CID = `Card`.id
                                INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                                WHERE (`OtherEventToCard`.EID = %s)"""
    
    tz_info = timezone(timedelta(hours=local['ver_time']))
    
    if event_type == 0:
        local['event'] = 'PSTEvent'
        local['other_params'] = ', type AS pst_type'
    elif event_type == 1:
        local['event'] = 'CollectEvent'
        local['other_params'] = ''
    elif event_type == 2:
        local['event'] = 'Anniversary'
        local['other_params'] = ''
    elif event_type == 3:
        local['event'] = 'WorkingEvent'
        local['other_params'] = ''
    elif event_type == 4:
        local['event'] = 'ShowTimeEvent'
        local['other_params'] = ''
    elif event_type == 5:
        local['event'] = 'OtherEvent'
        local['other_params'] = ''
    elif event_type == 6:
        local['event'] = 'TalkPartyEvent'
        local['other_params'] = ''
    else:
        raise NotFoundError
    
    sql_event_info = pre_sql_event_info.format(**local)
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_event_info, (event_id))
        event = cursor.fetchall()
        if not event:
            raise NotFoundError
        
        
        event = event[0]
        
        if event['start'] is None:
            return None
        
        event['is_jp'] = local['ver'] == 'jp'
        event['img_url'] = image_path('images/event_banner', '%d_%d.jpg' % (event_type, event_id))
        event['start'] = to_timestamp(event['start'], tz_info)
        event['over'] = to_timestamp(event['over'], tz_info)
        event['event_type'] = event_types[event_type][local['ver']]
        event['event_abbr'] = event_types[event_type]['abbr']
        event['pst_type'] = pst_types[event['pst_type']][local['ver']] if 'pst_type' in event and event['pst_type'] is not None else None
        
        if event_type == 0:
            card_types = [0, 1, 2]
            sql_event_card_pst = pre_sql_event_card_pst.format(**local)
            event['cards'] = {}
            for card_type in card_types:
                cursor.execute(sql_event_card_pst, (event_id, card_type))
                event['cards'][str(card_type)] = cursor.fetchall()
        elif event_type == 1:
            sql_event_card_col = pre_sql_event_card_col.format(**local)
            cursor.execute(sql_event_card_col, (event_id))
            event['cards'] = cursor.fetchall()
        elif event_type == 2:
            card_types = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            sql_event_card_ann = pre_sql_event_card_ann.format(**local)
            event['cards'] = {}
            for card_type in card_types:
                event['cards'][str(card_type)] = {'mission_date': event['start'] + timedelta(days=card_type).total_seconds() if event['start'] else None}
                cursor.execute(sql_event_card_ann, (event_id, card_type))
                event['cards'][str(card_type)]['data'] = cursor.fetchall()
                for card in event['cards'][str(card_type)]['data']:
                    if card['idol_name'] == 'エミリー スチュアート':
                        card['idol_name'] = 'エミリー'
        elif event_type == 5:
            sql_event_card_oth = pre_sql_event_card_oth.format(**local)
            cursor.execute(sql_event_card_oth, (event_id))
            event['cards'] = cursor.fetchall()
        else:
            connection.close()
            return event
        
    connection.close()
    if type(event['cards']) == list:
        for card in event['cards']:
            card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
            card['url'] = '/card/%d' % card['id']
            card['idol_type'] = idol_types[card['idol_type']]
    elif event_type == 2:
        for key in event['cards']:
            for card in event['cards'][key]['data']:
                card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
                card['url'] = '/card/%d' % card['id']
                card['idol_type'] = idol_types[card['idol_type']]
    else:
        for key in event['cards']:
            for card in event['cards'][key]:
                card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
                card['url'] = '/card/%d' % card['id']
                card['idol_type'] = idol_types[card['idol_type']]
    return event
    

def get_event_info(event_type, event_id):
    event = []
    event.append(get_event_info_local(event_type, event_id, jp_local))
    event.append(get_event_info_local(event_type, event_id, as_local))
    return event

def get_gasha_info_local(gasha_id, local):
    sql_gasha_info = """SELECT id, {name} AS name, 
                        {start} AS start, {over} AS over, type AS gasha_type, comment
                        FROM `Gasha` WHERE (id = %s)""".format(**local)
    sql_general_pick_up = """SELECT `Card`.id AS id, `Card`.{name} AS name, `GashaToCard`.comment AS comment,
                            `Card`.rare AS rare, `Idol`.type AS idol_type FROM `GashaToCard`
                             INNER JOIN `Card` ON `GashaToCard`.CID = `Card`.id
                             INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                             WHERE (`GashaToCard`.GID = %s)""".format(**local)
    pre_sql_general_others = """SELECT `Card`.id, `Card`.{name} AS name, `Card`.rare AS rare, `Idol`.type AS idol_type
                                FROM `Card` INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                                WHERE ({time} = %s AND aquire = 0 AND `Card`.id NOT IN ({id_values}))"""
    sql_special_draw = """SELECT `Card`.id, `Card`.{name} AS name, 
                          `GashaToCard`.comment AS comment, `Card`.rare AS rare, `Idol`.type AS idol_type
                          FROM `GashaToCard` INNER JOIN `Card` ON `GashaToCard`.CID = `Card`.id
                          INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                          WHERE (`GashaToCard`.GID = %s AND NOT `Card`.in_gasha = 2)""".format(**local)
    sql_special_others = """SELECT `Card`.id, `Card`.{name} AS name, 
                            `Card`.rare AS rare, `Idol`.type AS idol_type
                            FROM `GashaToCard` INNER JOIN `Card` ON `GashaToCard`.CID = `Card`.id
                            INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                            WHERE (`GashaToCard`.GID = %s AND `Card`.in_gasha = 2)""".format(**local)
    
    tz_info = timezone(timedelta(hours=local['ver_time']))
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_gasha_info, (gasha_id))
        gasha = cursor.fetchall()
        if not gasha:
            raise NotFoundError
        
        gasha = gasha[0]
        gasha['img_url'] = image_path('images/gasha_banners', '%d.jpg' % gasha['id'])
        
        if gasha['start'] is None:
            return None
        
        gasha['pick_up'] = []
        gasha['others'] = []
        
        if gasha['gasha_type'] == 5:
            cursor.execute(sql_special_draw, (gasha['id']))
            gasha['pick_up'] = cursor.fetchall()
            cursor.execute(sql_special_others, (gasha['id']))
            gasha['others'] = cursor.fetchall()
        else:
            cursor.execute(sql_general_pick_up, (gasha['id']))
            gasha['pick_up'] = cursor.fetchall()
            pick_up_ids = [card['id'] for card in gasha['pick_up']]
            g_local = loads(dumps(local))
            g_local['id_values'] = ', '.join(['%s'] * len(pick_up_ids))
            sql_general_others = pre_sql_general_others.format(**g_local)
            tuple_val = (gasha['start'],) + tuple(pick_up_ids)
            cursor.execute(sql_general_others, tuple_val)
            gasha['others'] = cursor.fetchall()
        
        for card in gasha['pick_up']:
            card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
            card['url'] = '/card/%d' % card['id']
            card['idol_type'] = idol_types[card['idol_type']]
        for card in gasha['others']:
            card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
            card['url'] = '/card/%d' % card['id']
            card['idol_type'] = idol_types[card['idol_type']]
        
        gasha['gasha_type'] = gasha_types[gasha['gasha_type']][local['ver']]
        gasha['start'] = to_timestamp(gasha['start'], tz_info)
        gasha['over'] = to_timestamp(gasha['over'], tz_info)
        
    connection.close()
    
    return gasha    

def get_gasha_info(gasha_id):
    gasha = []
    gasha.append(get_gasha_info_local(gasha_id, jp_local))
    gasha.append(get_gasha_info_local(gasha_id, as_local))
    return gasha

@app.route("/")
def home_page():
    return redirect('/idols')

@app.route("/idols")
def idols_page():
    idols = get_idols_info()
    return render_template('idols.html', idols=dumps(idols, ensure_ascii=False))

@app.route("/events")
def events_page():
    events, types = get_events_info()
    return render_template('events.html', events=dumps(events, ensure_ascii=False), types=dumps(types, ensure_ascii=False))

@app.route("/gashas")
def gashas_page():
    gashas, types = get_gashas_info()
    return render_template('gashas.html', gashas=dumps(gashas, ensure_ascii=False), types=dumps(types, ensure_ascii=False))

@app.route("/cards")
def cards_page():
    cards, filters = get_cards_info()
    return render_template('cards.html', cards=dumps(cards, ensure_ascii=False), filters=dumps(filters, ensure_ascii=False))

@app.route("/idol/<int:idol_id>")
def idol_page(idol_id):
    try:
        idol = get_idol_data(idol_id)
    except NotFoundError:
        abort(404)
    
    if idol[0] is not None:
        page_title = idol[0]['info']['name']
    else:
        page_title = idol[1]['info']['name']
    
    return render_template('idol.html', title=page_title, idol=dumps(idol, ensure_ascii=False))

@app.route("/card/<int:card_id>")
def card_page(card_id):
    try:
        card = get_card_info(card_id)
    except NotFoundError:
        abort(404)

    if card[0] is not None:
        page_title = rarity[card[0]['rare']] + ' ' + card[0]['name']
    else:
        page_title = rarity[card[1]['rare']] + ' ' + card[1]['name']
    return render_template('card.html', title=page_title, card=dumps(card, ensure_ascii=False))

@app.route("/event/<int:event_type>/<int:event_id>")
def event_page(event_type, event_id):
    try:
        event = get_event_info(event_type, event_id)
    except NotFoundError:
        abort(404)

    if event[0] is not None:
        page_title = event[0]['name']
    else:
        page_title = event[1]['name']
    return render_template('event.html', title=page_title, event=dumps(event, ensure_ascii=False))

@app.route("/gasha/<int:gasha_id>")
def gasha_page(gasha_id):
    try:
        gasha = get_gasha_info(gasha_id)
    except NotFoundError:
        abort(404)

    if gasha[0] is not None:
        page_title = gasha[0]['name']
    else:
        page_title = gasha[1]['name']
    return render_template('gasha.html', title=page_title, gasha=dumps(gasha, ensure_ascii=False))

@app.errorhandler(404)
def page_not_found(unused_error):
    return render_template('page_not_found.html'), 404


#app.run(host="0.0.0.0", port=5000)
