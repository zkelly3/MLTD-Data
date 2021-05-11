from dataclasses import asdict
from datetime import datetime, timezone, timedelta
from json import loads
import os.path

from flask import Flask
from flask import make_response, url_for, redirect, abort
from flask.json import dumps

from config import connect
from local import Local, jp_local, as_local

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
sort_types = [{'jp': '実装時間', 'as': '實裝時間', 'val': 'time'},
{'jp': 'レアリティ', 'as': '稀有度', 'val': 'rare'},
{'jp': 'アイドル', 'as': '偶像', 'val': 'idol_id'},
]
song_aquire_types = [{'jp': '初始', 'as': '初始'},
{'jp': 'PSTイベント', 'as': 'PST活動'},
{'jp': '周年イベント', 'as': '週年活動'},
{'jp': 'メインコミュ', 'as': '主線劇情'},
{'jp': '楽曲購入', 'as': '樂曲購買'},
{'jp': 'スペシャルコミュ', 'as': '特殊劇情'},
{'jp': 'その他', 'as': '其他'},
]

rarity = ['N', 'N＋', 'R', 'R＋', 'SR', 'SR＋', 'SSR', 'SSR＋']

def image_path(img_dir: str, img_name: str):
    img_path = os.path.join(img_dir, img_name)
    return url_for('static', filename=img_path)

def to_timestamp(target: datetime, tz_info: timezone):
    return target.replace(tzinfo=tz_info).timestamp() if target is not None else None

def get_idols_info_local(local: Local):
    sql_all_idols = """SELECT id, {name} AS name, type AS idol_type, 
                        CV, age, height, weight FROM Idol""".format_map(asdict(local))
    
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

def get_events_info_local(local: Local):
    sql_all_events = """SELECT id, {name} AS name, event_type,
                        {start} AS start, {over} AS `over` FROM `Event`
                        WHERE {start} IS NOT NULL ORDER BY {start} DESC""".format_map(asdict(local))
    
    tz_info = timezone(timedelta(hours=local.ver_time))

    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_all_events)
        events = cursor.fetchall()
    connection.close()
    
    for event in events:
        type_id = int(event.pop('event_type', len(event_types)))
        event_id = int(event.pop('id', 0))

        event['event_abbr'] = event_types[type_id]['abbr']
        event['url'] = '/event/%d' % event_id
        event['start'] = to_timestamp(event['start'], tz_info)
        event['over'] = to_timestamp(event['over'], tz_info)
    
    return events

def get_event_types_local(local: Local):
    types = []
    for event_type in event_types:
        types.append({
            'val': event_type['abbr'],
            'text': event_type[local.ver],
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

def get_gashas_info_local(local: Local):
    sql_all_gashas = """SELECT id, {name} AS name, type AS type_id, 
                        {start} AS start, {over} AS `over` FROM `Gasha`
                        WHERE {start} IS NOT NULL
                        ORDER BY {start} DESC""".format_map(asdict(local))
    
    tz_info = timezone(timedelta(hours=local.ver_time))

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

def get_gasha_types_local(local: Local):
    types = []
    for gasha_type in gasha_types:
        types.append({
            'val': gasha_type['abbr'],
            'text': gasha_type[local.ver],
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

def get_cards_info_local(local: Local):
    sql_all_cards = """SELECT `Card`.id AS id, `Card`.{name} AS name, `Card`.skill_val AS skill_val,
                       `Idol`.id AS idol_id, `Idol`.type AS idol_type, `Card`.card_id AS fake_id,
                       `Card`.rare AS rare, `Card`.{time} AS time, `Awaken`.id AS a_id, 
                       `Card`.aquire AS aquire, `Awaken`.aquire AS a_aquire,
                       `Card`.gasha_type AS gasha_type, `Awaken`.gasha_type AS a_gasha_type, 
                       `Card`.in_gasha AS in_gasha, `Awaken`.in_gasha AS a_in_gasha,
                       `SkillSubType`.SID AS skill_type, `LeaderSkill`.type AS l_skill_type
                       FROM `Card` LEFT JOIN `Idol` ON `Card`.IID = `Idol`.id
                       LEFT JOIN `Card` AS `Awaken` ON `Card`.awaken = `Awaken`.id
                       LEFT JOIN `SkillSubType` ON `Card`.skill_type = `SkillSubType`.id
                       LEFT JOIN `LeaderSkill` ON `Card`.leader_skill = `LeaderSkill`.id
                       WHERE `Card`.{time} IS NOT NULL
                       ORDER BY `Card`.{time} , `Card`.card_id""".format_map(asdict(local))
    sql_card_anniversary = """SELECT `Event`.fake_id AS EID FROM `EventToCard`
                              INNER JOIN `Event` ON `EventToCard`.EID = `Event`.id WHERE (CID = %s)"""
    
    tz_info = timezone(timedelta(hours=local.ver_time))
    
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
            
            skill_val = loads(card['skill_val']) if card['skill_val'] is not None else None
            card['skill_cd'] = skill_val['cd'] if skill_val is not None else None
            
    connection.close()    
    
    return cards

def get_cards_idols_local(local: Local):
    sql_all_idols = "SELECT id, {name} AS name, type AS idol_type FROM `Idol` WHERE {name} IS NOT NULL".format_map(asdict(local))
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_all_idols)
        res = cursor.fetchall()
    connection.close()
    
    idols = {}
    for idol in res:
        idol['img_url'] = image_path('images/idol_icons', '%d.png' % idol['id'])
        idols[idol['id']] = idol
    
    return idols

def get_cards_sorts_local(local: Local):
    sorts = [{'text': sort_type[local.ver], 'val': sort_type['val']} for sort_type in sort_types]
    
    return sorts

def get_card_filters_local(local: Local):
    sql_all_skills = "SELECT id, {name} AS name FROM `SkillType` WHERE {name} IS NOT NULL".format_map(asdict(local))
    sql_cards_skill_val = "SELECT skill_val FROM `Card` WHERE (skill_val IS NOT NULL)"
    
    filters = {}
    
    # 偶像陣營
    idol_labels = {'jp': '対象', 'as': '對象'}
    filters['belong'] = {
        'type': 'idol_check',
        'label': idol_labels[local.ver],
        'enabled': True,
        'type_options': ['Princess', 'Fairy', 'Angel', 'Guest'],
        'type_selected': [],
        'type_key': 'idol_type',
        'idol_enabled': False,
        'idol_selected': 1, # 天海春香
        'idol_key': 'idol_id',
    }
    
    # 稀有度
    rarity_labels = {'jp': 'レアリティ', 'as': '稀有度'}
    filters['rarity'] = {
        'type': 'check',
        'label': rarity_labels[local.ver],
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
        'label': awaken_labels[local.ver],
        'enabled': True,
        'options': [{'val': option['val'], 'text': option[local.ver]} for option in awaken_options],
        'selected': [True],
        'key': 'is_awaken',
    }
    
    # 卡片類型
    type_labels = {'jp': 'カテゴリ', 'as': '分類'}
    filters['card_type'] = {
        'type': 'check',
        'label': type_labels[local.ver],
        'enabled': True,
        'options': [{'val': option['abbr'], 'text': option[local.ver]} for option in card_types],
        'selected': [],
        'key': 'card_type',
    }
    
    connection = connect()
    with connection.cursor() as cursor:
        # 技能類型
        cursor.execute(sql_all_skills)
        skills = cursor.fetchall()
        skill_labels = {'jp': 'スキル', 'as': '技能'}
        filters['skill_type'] = {
            'type': 'check',
            'label': skill_labels[local.ver],
            'enabled': True,
            'options': [{'val': skill['id'], 'text': skill['name']} for skill in skills],
            'selected': [],
            'key': 'skill_type',
        }
        
        # Center效果類型
        l_skill_labels = {'jp': 'センター効果', 'as': 'Center效果'}
        filters['l_skill_type'] = {
            'type': 'check',
            'label': l_skill_labels[local.ver],
            'enabled': True,
            'options': [{'val': l_skill_type['val'], 'text': l_skill_type[local.ver]} for l_skill_type in l_skill_types],
            'selected': [],
            'key': 'l_skill_type',
        }
        
        # 技能 cd
        cursor.execute(sql_cards_skill_val)
        cards = cursor.fetchall()
        
        skill_cds = [loads(card['skill_val']).pop('cd', None) for card in cards]
        skill_cds = [val for val in skill_cds if val is not None]
        skill_cds = list(set(skill_cds))
        
        skill_cd_labels = {'jp': 'スキルクールタイム', 'as': '技能冷卻時間'}
        filters['skill_cd'] = {
            'type': 'check',
            'label': skill_cd_labels[local.ver],
            'enabled': True,
            'options': [{'val': skill_cd, 'text': str(skill_cd) + ' 秒'} for skill_cd in skill_cds],
            'selected': [],
            'key': 'skill_cd',
        }
        
    connection.close()
    
    return filters

def get_cards_info():
    cards = []
    cards.append(get_cards_info_local(jp_local))
    cards.append(get_cards_info_local(as_local))
    
    filters = []
    filters.append(get_card_filters_local(jp_local))
    filters.append(get_card_filters_local(as_local))
    
    sorts = []
    sorts.append(get_cards_sorts_local(jp_local))
    sorts.append(get_cards_sorts_local(as_local))
    
    idols = []
    idols.append(get_cards_idols_local(jp_local))
    idols.append(get_cards_idols_local(as_local))
    
    return cards, filters, sorts, idols

def get_songs_local(local: Local):
    sql_songs = """SELECT ANY_VALUE(`Song`.`id`) AS `id`,
                   ANY_VALUE(`Song`.`{name}`) AS `name`,
                   ANY_VALUE(`Song`.`resource`) AS `img_url`,
                   ANY_VALUE(`GameSound`.`{time}`) AS `time`,
                   ANY_VALUE(`IdolGroup`.`id`) AS `group_id`,
                   ANY_VALUE(`IdolGroup`.`{name}`) AS `group_name`
                   FROM `GameSound` LEFT JOIN `Sound`
                   ON `GameSound`.`SID` = `Sound`.`id`
                   LEFT JOIN `Song` ON `Sound`.`SID` = `Song`.`id`
                   LEFT JOIN `MainStory` ON `Song`.`id` = `MainStory`.`song`
                   LEFT JOIN `IdolGroup` ON `Sound`.`GID` = `IdolGroup`.`id`
                   WHERE (`GameSound`.`{time}` IS NOT NULL)
                   GROUP BY `Song`.`id`
                   ORDER BY ANY_VALUE(`GameSound`.`{time}`), 
                   ANY_VALUE(`Song`.`song_type`), ANY_VALUE(`MainStory`.`num`)""".format_map(asdict(local))
    sql_songs_group = """SELECT `Idol`.id, `Idol`.{name} AS name FROM `GroupToIdol`
                         LEFT JOIN `Idol` ON `GroupToIdol`.IID = `Idol`.id
                         WHERE (`GroupToIdol`.GID = %s)""".format_map(asdict(local)) 

    tz_info = timezone(timedelta(hours=local.ver_time))
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_songs)
        songs = cursor.fetchall()

        for song in songs:
            song['url'] = '/song/%d' % song['id']
            song['img_url'] = image_path('images/song_icons', 'jacket_%s.png' % song['img_url'])
            song['group_members'] = []
            group_id = song.pop('group_id', None)
            if group_id is not None:
                cursor.execute(sql_songs_group, (group_id))
                song['group_members'] = cursor.fetchall()
            if song['group_name'] is None:
                song['group_name'] = '、'.join([m['name'] for m in song['group_members']])
            song['time'] = to_timestamp(song['time'], tz_info)
    
    return songs

def get_songs():
    songs = []
    songs.append(get_songs_local(jp_local))
    songs.append(get_songs_local(as_local))

    return songs

def get_idol_info_local(idol_id: int, local: Local):
    sql_idol_info = """SELECT id, {name} AS name, type AS idol_type,
                  age, height, weight, CV, color
                  FROM `Idol` WHERE id = %s""".format_map(asdict(local))
    
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

def get_idol_cards_local(idol_id: int, local: Local):
    sql_idol_cards = """SELECT id, {name} AS name, rare, {time} AS time
                        FROM `Card` WHERE (IID = %s AND {time} IS NOT NULL)
                        ORDER BY {time}, card_id""".format_map(asdict(local))
    
    tz_info = timezone(timedelta(hours=local.ver_time))
    
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

def get_idol_data(idol_id: int):
    idol = []
    idol.append({'info': get_idol_info_local(idol_id, jp_local),
        'cards': get_idol_cards_local(idol_id, jp_local)})
    idol.append({'info': get_idol_info_local(idol_id, as_local),
        'cards': get_idol_cards_local(idol_id, as_local)})
    
    return idol

def get_card_aquire_local(card, card_id: int, aquire_id: int, local: Local, cursor):
    sql_gasha = """SELECT Gasha.id AS id, Gasha.{name} AS name,
                   Gasha.{start} AS start, Gasha.{over} AS `over`, Gasha.type AS gasha_type
                   FROM `GashaToCard` INNER JOIN `Gasha` ON GashaToCard.GID = Gasha.id
                   WHERE (GashaToCard.CID = %s AND Gasha.{start} IS NOT NULL)
                   ORDER BY Gasha.{start}""".format_map(asdict(local))
    sql_not_up = """SELECT id, {name} AS name, {start} AS start, {over} AS `over`, type AS gasha_type
                    FROM `Gasha` WHERE ({start} = %s AND NOT type = 5)""".format_map(asdict(local))
    sql_event = """SELECT `Event`.id AS id, `Event`.{name} AS name,
                   `Event`.{start} AS start, `Event`.{over} AS `over`,
                   `Event`.event_subtype aS event_subtype
                   FROM `EventToCard` INNER JOIN `Event` ON `EventToCard`.EID = `Event`.id
                   WHERE (`EventToCard`.CID = %s AND `Event`.{start} IS NOT NULL)
                   ORDER BY `Event`.{start}""".format_map(asdict(local))
    
    tz_info = timezone(timedelta(hours=local.ver_time))
    card['aquire'] = {'type': aquire_types[aquire_id][local.ver]} if aquire_id is not None else None

    guest_commu = {'jp': 'ゲストコミュ', 'as':'ゲストコミュ'}
    if card_id == 1455: # 世界に冠たる絶対女王　玲音
        card['from'] = 'Else'
        card['aquire']['title'] = guest_commu[local.ver]
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
            gasha['gasha_type'] = gasha_types[gasha['gasha_type']][local.ver]
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
        cursor.execute(sql_event, (card_id))
        event = cursor.fetchall()
        event = event[0] if event else None
        card['aquire']['title'] = event['name'] if event else None
        card['event'] = event
        
        if card['event'] is not None:
            card['has_from_url'] = True
            card['event']['url'] = '/event/%d' % event['id']
            card['from_url'] = card['event']['url']
            card['event']['start'] = to_timestamp(card['event']['start'], tz_info)
            card['event']['over'] = to_timestamp(card['event']['over'], tz_info)
            card['event']['event_type'] = pst_types[event['event_subtype']][local.ver] if aquire_id == 1 else aquire_types[aquire_id][local.ver]

def get_card_l_skill_local(card, card_id: int, rare_id: int, local: Local, cursor):
    sql_l_skill = """SELECT id, {name} AS name, {description} AS description, ssr, sr, r
                FROM `LeaderSkill` WHERE (id = %s)""".format_map(asdict(local))

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

def get_card_skill_local(card, card_id: int, rare_id: int, local: Local, cursor):
    sql_skill = """SELECT SkillType.id AS id, SkillType.{name} AS name,
                   SkillSubType.{description} AS description FROM `SkillSubType`
                   INNER JOIN `SkillType` ON SkillSubType.SID = SkillType.id
                   WHERE (SkillSubType.id = %s)""".format_map(asdict(local))

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

def get_card_info_local(card_id: int, local: Local):
    sql_card = """SELECT id, {name} AS name, IID, rare, {time} AS time, aquire, gasha_type, in_gasha,
                  {master_rank} AS master_rank, visual_max, vocal_max, dance_max,
                  visual_bonus, vocal_bonus, dance_bonus, leader_skill,
                  skill_type, {skill_name} AS skill_name, skill_val,
                  {flavor} AS flavor, awaken
                  FROM `Card` WHERE (id = %s)""".format_map(asdict(local))
    sql_idol = "SELECT {name} AS name, color, type AS idol_type FROM `Idol` WHERE (id = %s)".format_map(asdict(local))
    sql_awaken = "SELECT id, {name} AS name FROM `Card` WHERE (id = %s)".format_map(asdict(local))

    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_card, (card_id))
        card = cursor.fetchall()
        if not card:
            raise NotFoundError

        card = card[0]
        card['is_jp'] = local.ver == 'jp'

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

        tz_info = timezone(timedelta(hours=local.ver_time))
        card['time'] = to_timestamp(card['time'], tz_info)
        card['img_url'] = image_path('images/card_images', '%d.png' % card['id'])
        if rare_id >= 6:
            card['big_img_url'] = image_path('images/card_images_bg/', '%d.png' % card['id'])
        
    connection.close()
    return card

def get_card_info(card_id: int):
    card = []
    card.append(get_card_info_local(card_id, jp_local))
    card.append(get_card_info_local(card_id, as_local))
    return card

def get_card_title_local(card_id: int, local: Local):
    sql_get_card_title = "SELECT {name} AS name, rare FROM `Card` WHERE (id = %s AND {name} IS NOT NULL)".format_map(asdict(local))

    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_get_card_title, (card_id))
        card = cursor.fetchall()
    connection.close()

    if not card:
        return None
    card = card[0]
    return rarity[card['rare']] + ' ' + card['name']

def get_card_title(card_id: int):
    jp_title = get_card_title_local(card_id, jp_local)
    as_title = get_card_title_local(card_id, as_local)
    return jp_title if jp_title is not None else as_title 

def get_event_info_local(event_id: int, local: Local):
    sql_event_info = """SELECT id, {name} AS name, 
                        {start} AS start, {over} AS `over`, event_type, fake_id, event_subtype, comment
                        FROM `Event` WHERE (id = %s)""".format_map(asdict(local))
    sql_event_cards_type_y = """SELECT `Card`.id AS id, `Card`.{name} AS name,
                              `Card`.rare AS rare, `Idol`.type AS idol_type, `Idol`.{name} As idol_name
                              FROM `EventToCard` INNER JOIN `Card`
                              ON `EventToCard`.CID = `Card`.id
                              INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                              WHERE (`EventToCard`.EID = %s AND `EventToCard`.card_type = %s)""".format_map(asdict(local))
    sql_event_cards_type_n = """SELECT `Card`.id AS id, `Card`.{name} AS name,
                              `Card`.rare AS rare, `Idol`.type AS idol_type
                              FROM `EventToCard` INNER JOIN `Card`
                              ON `EventToCard`.CID = `Card`.id
                              INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                              WHERE (`EventToCard`.EID = %s) ORDER BY `EventToCard`.card_type""".format_map(asdict(local))


    tz_info = timezone(timedelta(hours=local.ver_time))
    card_types = [[0, 1, 2], [], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], None, None, [], None]
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_event_info, (event_id))
        event = cursor.fetchall()
        if not event:
            raise NotFoundError
        
        event = event[0]
        if event['start'] is None:
            return None
        
        event_type = event.pop('event_type', len(event_types))
        fake_id = event.pop('fake_id', 0)
        event_subtype = event.pop('event_sub', None)

        event['is_jp'] = local.ver == 'jp'
        event['img_url'] = image_path('images/event_banner', '%d_%d.jpg' % (event_type, fake_id))
        event['start'] = to_timestamp(event['start'], tz_info)
        event['over'] = to_timestamp(event['over'], tz_info)
        event['event_type'] = event_types[event_type][local.ver]
        event['event_abbr'] = event_types[event_type]['abbr']
        event['pst_type'] = pst_types[event_subtype][local.ver] if event_subtype else None

        if card_types[event_type] is not None:
            if not card_types[event_type]:
                # 百萬收藏、其他
                cursor.execute(sql_event_cards_type_n, (event_id))
                event['cards'] = cursor.fetchall()
                for card in event['cards']:
                    card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
                    card['url'] = '/card/%d' % card['id']
                    card['idol_type'] = idol_types[card['idol_type']]
            elif event_type == 2:
                # 週年
                event['cards'] = {}
                for card_type in card_types[event_type]:
                    event['cards'][str(card_type)] = {'mission_date': event['start'] + timedelta(days=card_type).total_seconds() if event['start'] else None}
                    cursor.execute(sql_event_cards_type_y, (event_id, card_type))
                    event['cards'][str(card_type)]['data'] = cursor.fetchall()
                    for card in event['cards'][str(card_type)]['data']:
                        if card['idol_name'] == 'エミリー スチュアート':
                            card['idol_name'] = 'エミリー'
                        card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
                        card['url'] = '/card/%d' % card['id']
                        card['idol_type'] = idol_types[card['idol_type']]
            else:
                # PST
                event['cards'] = {}
                for card_type in card_types[event_type]:
                    cursor.execute(sql_event_cards_type_y, (event_id, card_type))
                    event['cards'][str(card_type)] = cursor.fetchall()
                    for card in event['cards'][str(card_type)]:
                        card.pop('idol_name')
                        card['img_url'] = image_path('images/card_icons', '%d.png' % card['id'])
                        card['url'] = '/card/%d' % card['id']
                        card['idol_type'] = idol_types[card['idol_type']]
        
    connection.close()
    return event

def get_event_info(event_id: int):
    event = []
    event.append(get_event_info_local(event_id, jp_local))
    event.append(get_event_info_local(event_id, as_local))
    return event

def get_gasha_info_local(gasha_id: int, local: Local):
    sql_gasha_info = """SELECT id, {name} AS name, 
                        {start} AS start, {over} AS `over`, type AS gasha_type, comment
                        FROM `Gasha` WHERE (id = %s)""".format_map(asdict(local))
    sql_general_pick_up = """SELECT `Card`.id AS id, `Card`.{name} AS name, `GashaToCard`.comment AS comment,
                            `Card`.rare AS rare, `Idol`.type AS idol_type FROM `GashaToCard`
                             INNER JOIN `Card` ON `GashaToCard`.CID = `Card`.id
                             INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                             WHERE (`GashaToCard`.GID = %s)""".format_map(asdict(local))
    pre_sql_general_others = """SELECT `Card`.id, `Card`.{name} AS name, `Card`.rare AS rare, `Idol`.type AS idol_type
                                FROM `Card` INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                                WHERE ({time} = %s AND aquire = 0 AND `Card`.id NOT IN ({id_values}))"""
    sql_special_draw = """SELECT `Card`.id, `Card`.{name} AS name, 
                          `GashaToCard`.comment AS comment, `Card`.rare AS rare, `Idol`.type AS idol_type
                          FROM `GashaToCard` INNER JOIN `Card` ON `GashaToCard`.CID = `Card`.id
                          INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                          WHERE (`GashaToCard`.GID = %s AND NOT `Card`.in_gasha = 2)""".format_map(asdict(local))
    sql_special_others = """SELECT `Card`.id, `Card`.{name} AS name, 
                            `Card`.rare AS rare, `Idol`.type AS idol_type
                            FROM `GashaToCard` INNER JOIN `Card` ON `GashaToCard`.CID = `Card`.id
                            INNER JOIN `Idol` ON `Card`.IID = `Idol`.id
                            WHERE (`GashaToCard`.GID = %s AND `Card`.in_gasha = 2)""".format_map(asdict(local))
    
    tz_info = timezone(timedelta(hours=local.ver_time))
    
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
            g_local = asdict(local)
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
        
        gasha['gasha_type'] = gasha_types[gasha['gasha_type']][local.ver]
        gasha['start'] = to_timestamp(gasha['start'], tz_info)
        gasha['over'] = to_timestamp(gasha['over'], tz_info)
        
    connection.close()
    
    return gasha    

def get_gasha_info(gasha_id: int):
    gasha = []
    gasha.append(get_gasha_info_local(gasha_id, jp_local))
    gasha.append(get_gasha_info_local(gasha_id, as_local))
    return gasha

def get_song_info_local(song_id: int, local: Local):
    sql_song_info = """SELECT id, {name} AS name, `type` AS idol_type, resource AS img_url
                       FROM `Song` WHERE (id = %s)""".format_map(asdict(local))
    sql_song_sound = """SELECT `GameSound`.id AS id, `GameSound`.{time} AS time,
                        `Sound`.GID AS group_id, `IdolGroup`.{name} AS group_name
                        FROM `GameSound` LEFT JOIN `Sound`
                        ON `GameSound`.`SID` = `Sound`.id
                        LEFT JOIN `IdolGroup` ON `Sound`.GID = `IdolGroup`.id
                        WHERE (`Sound`.SID = %s AND `GameSound`.{time} IS NOT NULL)
                        ORDER BY `GameSound`.{time}""".format_map(asdict(local))
    sql_song_group_members = """SELECT `Idol`.{name} AS name FROM `GroupToIdol`
                           LEFT JOIN `Idol` ON `GroupToIdol`.IID = `Idol`.id
                           WHERE `GroupToIdol`.GID = %s""".format_map(asdict(local))

    tz_info = timezone(timedelta(hours=local.ver_time))
    
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_song_info, (song_id))
        song = cursor.fetchall()
        if not song:
            raise NotFoundError
        
        song = song[0]
        song['idol_type'] = idol_types[song['idol_type']]
        song['img_url'] = image_path('images/song_icons', 'jacket_%s.png' % song['img_url']) if song['img_url'] is not None else ''
        cursor.execute(sql_song_sound, (song_id))
        song['sound'] = cursor.fetchall()
        song['time'] = song['sound'][0]['time'] if song['sound'] else None
        if song['time'] is None:
            return None

        song['time'] = to_timestamp(song['time'], tz_info)
        for sound in song['sound']:
            group_id = sound.pop('group_id', 0)
            if sound['group_name'] is None:
                cursor.execute(sql_song_group_members, (group_id))
                members = cursor.fetchall()
                sound['group_name'] = '、'.join([member['name'] for member in members])
            sound['time'] = to_timestamp(sound['time'], tz_info)
    connection.close()

    return song

def get_song_info(song_id: int):
    song = []
    song.append(get_song_info_local(song_id, jp_local))
    song.append(get_song_info_local(song_id, as_local))
    
    return song

@app.route("/api/idols")
def idols_api():
    idols = get_idols_info()
    return dumps(idols)

@app.route("/api/events")
def events_api():
    events, types = get_events_info()
    return dumps(events, ensure_ascii=False)

@app.route("/api/events/types")
def event_types_api():
    events, types = get_events_info()
    return dumps(types, ensure_ascii=False)

@app.route("/api/gashas")
def gashas_api():
    gashas, types = get_gashas_info()
    return dumps(gashas, ensure_ascii=False)

@app.route("/api/gashas/types")
def gasha_types_api():
    gashas, types = get_gashas_info()
    return dumps(types, ensure_ascii=False)

@app.route("/api/cards")
def cards_api():
    cards, filters, sorts, idols = get_cards_info()
    return dumps(cards, ensure_ascii=False)

@app.route("/api/cards/filters")
def card_filters_api():
    cards, filters, sorts, idols = get_cards_info()
    return dumps(filters, ensure_ascii=False)

@app.route("/api/cards/sorts")
def card_sorts_api():
    cards, filters, sorts, idols = get_cards_info()
    return dumps(sorts, ensure_ascii=False)

@app.route("/api/cards/idols")
def card_idols_api():
    cards, filters, sorts, idols = get_cards_info()
    return dumps(idols, ensure_ascii=False)

@app.route("/api/songs")
def songs_api():
    songs = get_songs()
    return dumps(songs, ensure_ascii=False)

@app.route("/api/idol/<int:idol_id>")
def idol_api(idol_id: int):
    try:
        idol = get_idol_data(idol_id)
    except NotFoundError:
        abort(404)

    return dumps(idol, ensure_ascii=False)

@app.route("/api/card/<int:card_id>")
def card_api(card_id: int):
    try:
        card = get_card_info(card_id)
    except NotFoundError:
        abort(404)
    return dumps(card, ensure_ascii=False)

@app.route("/api/card/title/<int:card_id>")
def card_title_api(card_id: int):
    return get_card_title(card_id)

@app.route("/api/event/<int:event_id>")
def event_api(event_id: int):
    try:
        event = get_event_info(event_id)
    except NotFoundError:
        abort(404)
    return dumps(event, ensure_ascii=False)

@app.route("/api/gasha/<int:gasha_id>")
def gasha_api(gasha_id: int):
    try:
        gasha = get_gasha_info(gasha_id)
    except NotFoundError:
        abort(404)
    return dumps(gasha, ensure_ascii=False)

@app.route("/api/song/<int:song_id>")
def song_api(song_id: int):
    try:
        song = get_song_info(song_id)
    except NotFoundError:
        abort(404)
    return dumps(song, ensure_ascii=False)

@app.errorhandler(404)
def page_not_found(unused_error):
    return make_response(dumps({}), 404)


#app.run(host="0.0.0.0", port=5000)
