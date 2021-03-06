from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import IntEnum
import json
import re
import os.path
import argparse
import requests

import config
from db import Database, NotFoundError
from dry_cursor import DryCursor
from fix_json import get_idol_names, handle_data

errors = []

def craw_card(write_type, name, img_url, img_path):
    if not os.path.isfile(img_path):
        img_data = requests.get(img_url).content
        print('Write', write_type, name)
        with open(img_path, 'wb') as handler:
            handler.write(img_data)

def get_iid(name, db, is_jp):
    idol = name.split('　')[-1]
    # 特判掉艾蜜莉
    if is_jp and idol == 'エミリー':
        idol = 'エミリー スチュアート'

    return db.get_card_iid(name=idol)

def craw_aquire(url):
    # aquire = [卡池, PST, 百萬收藏, 初始, 周年, 覺醒, 其他]
    # gashatype = [不限制, 期間限定, FES]
    # ingasha = [一直能抽, 有時能抽, 不能抽]


    # 活動相關
    span = config.bs4_data(url, string=re.compile('.*イベント:.*'))
    if span:
        words = span[0].parent.text
        gashatype = 0
        ingasha = 2
        if re.search('プラチナスター', words):
            # PST
            aquire = 1
        elif re.search('ミリコレ', words):
            # 百萬收藏
            aquire = 2
        elif re.search('エイプリルフール', words):
            # 其他 (愚人節小活動)
            aquire = 6
        else:
            # 暫定只有周年活動會進
            aquire = 4
        return aquire, gashatype, ingasha

    # 卡池相關
    span = config.bs4_data(url, string=re.compile('.*ガシャ種別:.*'))
    if span:
        words = span[0].parent.text
        aquire = 0
        if re.search('恒常', words):
            # 常駐
            gashatype = 0
            ingasha = 0
        elif re.search('期間限定', words):
            # 期間限定
            gashatype = 1
            ingasha = 1
        elif re.search('フェス限定', words):
            # FES
            gashatype = 2
            ingasha = 1
        elif re.search('ピックアップ SR ', words):
            # 特殊 SR 卡池
            gashatype = 1
            ingasha = 1
        else:
            # 暫定只有特殊抽卡券會進
            gashatype = 0
            ingasha = 2
        return aquire, gashatype, ingasha

    # 暫時認為不會有初始卡在這裡
    aquire = 6
    gashatype = 0
    ingasha = 2
    return aquire, gashatype, ingasha

def handle_l_skill(card_id, info_0, info_1, is_jp, db):
    url = os.path.join(config.card_info_root_url if is_jp else config.as_card_info_root_url, str(card_id))
    span = config.bs4_data(url, 'span', string='センター効果' if is_jp else 'Leader Skill')
    if span:
        has_ls, ls_str = config.consume(span[0].parent.text, 'センター効果' if is_jp else 'Leader Skill')
        if has_ls:
            try:
                lskill_id = db.get_card_lskill_id(name=ls_str)
                db.update_cards([info_0, info_1], leader_skill=lskill_id)
            except NotFoundError:
                err = 'Something wrong in leader skill string for ' + info_0.name
                errors.append(err)
        else:
            err = 'Fail to extract leader skill for ' + info_0.name
            errors.append(err)
    else:
        err = 'No leader skill for ' + info_0.name
        errors.append(err)

def craw_values(url, name, is_jp):
    global errors
    res_0 = {}
    res_1 = {}
    if is_jp:
        todos = [{'key': 'visual', 'target': 'ビジュアル'},
            {'key': 'vocal', 'target': 'ボーカル'},
            {'key': 'dance', 'target': 'ダンス'}]
    else:
        todos = [{'key': 'visual', 'target': 'Visual'},
            {'key': 'vocal', 'target': 'Vocal'},
            {'key': 'dance', 'target': 'Dance'}]

    for todo in todos:
        spans = config.bs4_data(url, 'span', string=todo['target'])
        if len(spans) < 2:
            errors.append('Value ' + todo['target'] + ' for ' + name + ' not found')
            return None, None
        has_value, value = config.consume(spans[0].parent.text, todo['target'])
        if has_value:
            res_0[todo['key']] = int(value.split('(')[0].strip())
        else:
            res_0[todo['key']] = None
        has_value, value = config.consume(spans[1].parent.text, todo['target'])
        if has_value:
            res_1[todo['key']] = int(value.split('(')[0].strip())
        else:
            res_1[todo['key']] = None
    return res_0, res_1

def craw_flavor(url, name, is_jp):
    global errors
    target = 'フレーバーテキスト' if is_jp else 'Flavor text'
    spans = config.bs4_data(url, 'span', string=target)
    if len(spans) < 2:
        errors.append('Flavor Text for ' + name + ' not found')
        return None, None
    has_value, value = config.consume(spans[0].parent.text, target)
    res_0 = value if has_value else None
    has_value, value = config.consume(spans[1].parent.text, target)
    res_1 = value if has_value else None
    return res_0, res_1

class Rarity(IntEnum):
    N = 0
    NP = 1
    R = 2
    RP = 3
    SR = 4
    SRP = 5
    SSR = 6
    SSRP = 7

@dataclass
class CardInfo:
    name: str
    rarity: Rarity
    id: int = -1

class EffectId(IntEnum):
    SCORE_UP = 1
    COMBO_BONUS = 2
    LIFE_RECOVER = 3
    LIFE_GUARD = 4
    COMBO_CONTINUE = 5
    PERFECTLIZE = 6
    SCORE_UP_COMBO_BONUS = 7
    MULTI_UP = 8
    DAMAGE_SCORE_UP = 10
    DAMAGE_COMBO_BONUS = 11

class SubType(IntEnum):
    SCORE_UP_PG = 1
    SCORE_UP_P = 2
    COMBO_BONUS = 3
    LIFE_RECOVER = 4
    LIFE_GUARD = 5
    COMBO_CONTINUE = 6
    PERFECTLIZE_GGFS = 7
    PERFECTLIZE_GG = 8
    PERFECTLIZE_G = 9
    SCORE_UP_COMBO_BONUS = 10
    MULTI_UP = 11
    DAMAGE_SCORE_UP = 12
    DAMAGE_COMBO_BONUS = 13

def get_sub_type(eff_id, rarity):
    eff_id = EffectId(eff_id)
    try:
        if eff_id == EffectId.SCORE_UP:
            return SubType.SCORE_UP_PG if rarity == Rarity.SSR else SubType.SCORE_UP_P
        if eff_id == EffectId.PERFECTLIZE:
            return {
                Rarity.SSR: SubType.PERFECTLIZE_GGFS,
                Rarity.SR: SubType.PERFECTLIZE_GG,
                Rarity.R: SubType.PERFECTLIZE_G,
            }[rarity]
        return SubType[eff_id.name]
    except KeyError as e:
        raise NotFoundError from e

def get_or_insert_card_entry(card, db, data, is_jp, info_0, info_1):
    try:
        if not is_jp and card['id'] < 9000:
            jp_name = ''
            for jp_card in data:
                if card['id'] == jp_card['id']:
                    jp_name = jp_card['name']
                    break
            return db.get_card_info(jp_name=jp_name)
        return db.get_card_info(name=info_0.name)
    except NotFoundError:
        # 新增卡片到資料庫
        idol_id = get_iid(info_0.name, db, is_jp)

        print('Inserting card', info_0.name)
        db.insert_card(name=info_0.name, IID=idol_id, rare=int(info_0.rarity))
        print('Inserting card', info_1.name)
        db.insert_card(name=info_1.name, IID=idol_id, rare=int(info_1.rarity))

        return db.get_card_info(name=info_0.name)

def handle_card(card, db, data, is_jp):
    global errors

    info_0 = CardInfo(name = card['name'], rarity = Rarity((card['rarity'] - 1) * 2))
    info_1 = CardInfo(name = info_0.name + '＋', rarity = info_0.rarity + 1)

    print('Start', info_0.name)

    # 在資料庫找到這張卡
    try:
        row = get_or_insert_card_entry(card, db, data, is_jp, info_0, info_1)
    except NotFoundError:
        errors.append(info_0.name + ' not found')
        return

    info_0.id = row['id']

    # 設定未覺醒和覺醒的配對
    if row['awaken'] is None:
        try:
            info_1.id = db.get_card_info(name=info_1.name)['id']
        except NotFoundError:
            err = 'Awaken ' + info_1.name + ' not found'
            errors.append(err)
            return

        db.update_card(info_0, awaken=info_1.id)
        db.update_card(info_1, awaken=info_0.id)
    else:
        info_1.id = row['awaken']

    # 處理中文卡片名稱
    if not is_jp and row['as_name'] is None:
        db.update_card(info_0, name=info_0.name)
        db.update_card(info_1, name=info_1.name)

    # 處理沒有輸入偶像的情況
    if row['IID'] is None:
        idol_id = get_iid(info_0.name, db, is_jp)
        db.update_cards([info_0, info_1], IID=idol_id)

    # 抓卡片實裝時間
    old_time = row['jp_time'] if is_jp else row['as_time']
    if old_time is None:
        url = os.path.join(config.card_info_root_url if is_jp else config.as_card_info_root_url, str(card['id']))
        span = config.bs4_data(url, 'span', class_='intl-date-dyts')
        if span:
            new_time = datetime.fromtimestamp(int(span[0]['data-date']) / 1000, timezone(timedelta(hours=9 if is_jp else 8)))

            db.update_cards([info_0, info_1], time=new_time)
        else:
            err = 'No time for ' + info_0.name
            errors.append(err)


    # 處理 Center 效果
    if info_0.rarity != Rarity.N and row['leader_skill'] is None:
        handle_l_skill(card['id'], info_0, info_1, is_jp, db)

    # 處理技能
    if info_0.rarity != Rarity.N:
        if row['skill_type'] is None:
            skill = card['skills'][0]
            s_val = {
                'cd': skill['interval'],
                'prob': skill['probability'],
                'dur': skill['duration'],
                'val': []
            }
            for val in skill['value']:
                s_val['val'].append(val)

            try:
                s_type = int(get_sub_type(skill['effectId'], info_0.rarity))
            except NotFoundError:
                err = 'Error transposing skill type for ' + info_0.name
                errors.append(err)
                s_type = -1

            s_name = ''
            url = os.path.join(config.card_info_root_url if is_jp else config.as_card_info_root_url, str(card['id']))
            span = config.bs4_data(url, 'span', string='スキル' if is_jp else 'Skill')
            if span:
                has_sn, sn_str = config.consume(span[0].parent.text, 'スキル' if is_jp else 'Skill')
                if has_sn:
                    s_name = sn_str
                else:
                    err = 'Fail to extract skill name for ' + info_0.name
                    errors.append(err)
            else:
                err = 'No skill name for ' + info_0.name
                errors.append(err)

            db.update_cards([info_0, info_1], skill_type=s_type,
                            skill_name=s_name, skill_val=json.dumps(s_val))
        elif not is_jp and not row['as_skill_name']:
            s_name = ''
            url = os.path.join(config.as_card_info_root_url, str(card['id']))
            span = config.bs4_data(url, 'span', string='Skill')
            if span:
                has_sn, sn_str = config.consume(span[0].parent.text, 'Skill')
                if has_sn:
                    s_name = sn_str
                else:
                    err = 'Fail to extract skill name for ' + info_0.name
                    errors.append(err)
            else:
                err = 'No skill name for ' + info_0.name
                errors.append(err)

            db.update_cards([info_0, info_1], skill_name=s_name)

    # 處理取得方式等等
    if row['aquire'] is None:
        url = os.path.join(config.card_info_root_url if is_jp else config.as_card_info_root_url, str(card['id']))
        aquire, gasha_type, in_gasha = craw_aquire(url)
        db.update_card(info_0, aquire=aquire, gasha_type=gasha_type, in_gasha=in_gasha)
        db.update_card(info_1, aquire=5, gasha_type=gasha_type, in_gasha=2)

    # 處理卡片數值
    if row['visual_max'] is None:
        url = os.path.join(config.card_info_root_url if is_jp else config.as_card_info_root_url, str(card['id']))
        vals_0, vals_1 = craw_values(url, info_0.name, is_jp)
        if vals_0 is not None and vals_1 is not None:
            db.update_card(info_0, visual_max=vals_0['visual'],
                           vocal_max=vals_0['vocal'], dance_max=vals_0['dance'])
            db.update_card(info_1, visual_max=vals_1['visual'],
                           vocal_max=vals_1['vocal'], dance_max=vals_1['dance'])

    # 處理突破 Bonus
    if row['visual_bonus'] is None or str(card['masterRankMax']) not in json.loads(row['visual_bonus']):
        master_rank = str(card['masterRankMax'])
        vi_bonus = {} if row['visual_bonus'] is None else json.loads(row['visual_bonus'])
        vo_bonus = {} if row['vocal_bonus'] is None else json.loads(row['vocal_bonus'])
        da_bonus = {} if row['dance_bonus'] is None else json.loads(row['dance_bonus'])
        vi_bonus[master_rank] = card['visualMasterBonus']
        vo_bonus[master_rank] = card['vocalMasterBonus']
        da_bonus[master_rank] = card['danceMasterBonus']

        db.update_cards([info_0, info_1], visual_bonus=json.dumps(vi_bonus),
                        vocal_bonus=json.dumps(vo_bonus), dance_bonus=json.dumps(da_bonus))

    # 處理最大突破
    if is_jp and row['jp_master_rank'] is None:
        db.update_cards([info_0, info_1], master_rank=card['masterRankMax'])
    elif not is_jp and row['as_master_rank'] is None:
        db.update_cards([info_0, info_1], master_rank=card['masterRankMax'])

    # 處理背景敘述
    if is_jp and row['jp_flavor'] is None:
        url = os.path.join(config.card_info_root_url, str(card['id']))
        flavor_0, flavor_1 = craw_flavor(url, info_0.name, is_jp)
        if flavor_0 is not None and flavor_1 is not None:
            db.update_card(info_0, flavor=flavor_0)
            db.update_card(info_1, flavor=flavor_1)
    elif not is_jp and row['as_flavor'] is None:
        url = os.path.join(config.as_card_info_root_url, str(card['id']))
        flavor_0, flavor_1 = craw_flavor(url, info_0.name, is_jp)
        if flavor_0 is not None and flavor_1 is not None:
            db.update_card(info_0, flavor=flavor_0)
            db.update_card(info_1, flavor=flavor_1)

    # 處理假 id
    if is_jp and row['card_id'] is None:
        db.update_card(info_0, card_id=card['id'])
        db.update_card(info_1, card_id=card['id'])

    # 爬 icon 圖
    icon_url_0 = os.path.join(config.icon_root_url, card['resourceId'] + '_0.png') if is_jp else os.path.join(config.as_icon_root_url, card['resourceId'] + '_0.png')
    icon_path_0 = os.path.join(config.icon_dir, str(info_0.id) + '.png')
    icon_url_1 = os.path.join(config.icon_root_url, card['resourceId'] + '_1.png') if is_jp else os.path.join(config.as_icon_root_url, card['resourceId'] + '_1.png')
    icon_path_1 = os.path.join(config.icon_dir, str(info_1.id) + '.png')

    craw_card('icon', info_0.name, icon_url_0, icon_path_0)
    craw_card('icon', info_1.name, icon_url_1, icon_path_1)

    # 爬卡面
    card_url_0 = os.path.join(config.card_root_url, card['resourceId'] + '_0_b.png') if is_jp else os.path.join(config.as_card_root_url, card['resourceId'] + '_0_b.png')
    card_path_0 = os.path.join(config.card_dir, str(info_0.id) + '.png')
    card_url_1 = os.path.join(config.card_root_url, card['resourceId'] + '_1_b.png') if is_jp else os.path.join(config.as_card_root_url, card['resourceId'] + '_1_b.png')
    card_path_1 = os.path.join(config.card_dir, str(info_1.id) + '.png')

    craw_card('card', info_0.name, card_url_0, card_path_0)
    craw_card('card', info_1.name, card_url_1, card_path_1)

    # 爬 SSR 大圖
    if info_0.rarity == Rarity.SSR:
        bg_url_0 = os.path.join(config.bg_root_url, card['resourceId'] + '_0.png') if is_jp else os.path.join(config.as_bg_root_url, card['resourceId'] + '_0.png')
        bg_path_0 = os.path.join(config.bg_dir, str(info_0.id) + '.png')
        bg_url_1 = os.path.join(config.bg_root_url, card['resourceId'] + '_1.png') if is_jp else os.path.join(config.as_bg_root_url, card['resourceId'] + '_1.png')
        bg_path_1 = os.path.join(config.bg_dir, str(info_1.id) + '.png')

        craw_card('bg', info_0.name, bg_url_0, bg_path_0)
        craw_card('bg', info_1.name, bg_url_1, bg_path_1)

    print('Finish card', info_0.name)

def main():
    global errors
    
    parser = argparse.ArgumentParser(description='Arguments for crawcards.py')
    parser.add_argument('--real', action="store_true", default=False, help='real run')    
    args = parser.parse_args()

    
    idol_jp_names, idol_as_names = get_idol_names()
    
    with open('cards.json') as f:
        data = json.load(f)
        handle_data(data, idol_jp_names, 'jp')

    with open('ascards.json') as f:
        as_data = json.load(f)
        handle_data(as_data, idol_as_names, 'as')

    connection = config.connect()

    with connection.cursor() as cursor:
        if not args.real:
            cursor = DryCursor(cursor)

        # 更新 (日版) 卡片資訊
        for card in data:
            if card['extraType'] in [5, 7, 10] and card['rarity'] == 4:
                continue
            handle_card(card, Database(cursor, is_jp=True), data, True)

        # 更新 (海外版) 卡片資訊
        for card in as_data:
            if card['extraType'] in [5, 7, 10] and card['rarity'] == 4:
                continue
            handle_card(card, Database(cursor, is_jp=False), data, False)

    connection.close()



    print('Errors:')
    for error in errors:
        print(error)


if __name__ == '__main__':
    main()
