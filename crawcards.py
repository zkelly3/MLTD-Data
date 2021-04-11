from datetime import datetime, timezone, timedelta
from enum import IntEnum
import json
import re
import os.path

import requests

import config
from dry_cursor import DryCursor

get_card_info = config.get_card_info_tmp.format(name="jp_name")
get_card_info_as = config.get_card_info_tmp.format(name="as_name")

errors = []

class NotFoundError(Exception):
    pass

def craw_card(write_type, name, img_url, img_path):
    if not os.path.isfile(img_path):
        img_data = requests.get(img_url).content
        print('Write', write_type, name)
        with open(img_path, 'wb') as handler:
            handler.write(img_data)

def get_iid(name, cursor, is_jp):
    idol = name.split('　')[-1]
    # 特判掉艾蜜莉
    if is_jp and idol == 'エミリー':
        idol = 'エミリー スチュアート'

    cursor.execute(config.get_card_iid if is_jp else config.get_card_iid_as, (idol))
    return cursor.fetchall()[0]['id']

def edit_name(name):
    guess = ['　', ' ']
    res = name
    for i in range(len(name)-1, -1, -1):
        if name[i] in guess:
            res = name[:i] + '　' + name[i+1:]
            break
    return res

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

def handle_l_skill(card_id, id_0, id_1, name, name_1, is_jp, cursor):
    url = os.path.join(config.card_info_root_url if is_jp else config.as_card_info_root_url, str(card_id))
    span = config.bs4_data(url, 'span', string='センター効果' if is_jp else 'Leader Skill')
    if span:
        has_ls, ls_str = config.consume(span[0].parent.text, 'センター効果' if is_jp else 'Leader Skill')
        if has_ls:
            if is_jp:
                cursor.execute(config.get_card_lsid, (ls_str))
            else:
                cursor.execute(config.get_card_lsid_as, (ls_str))
            res = cursor.fetchall()
            if res:
                ls_id = res[0]['id']
                print('Set leader skill for', name)
                cursor.execute(config.set_card_lsid, (ls_id, id_0))
                cursor.connection.commit()
                print('Set leader skill for', name_1)
                cursor.execute(config.set_card_lsid, (ls_id, id_1))
                cursor.connection.commit()
            else:
                err = 'Something wrong in leader skill string for ' + name
                errors.append(err)
        else:
            err = 'Fail to extract leader skill for ' + name
            errors.append(err)
    else:
        err = 'No leader skill for ' + name
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
    
def get_sub_type(eff_id, rare_0):
    eff_id = EffectId(eff_id)
    try:
        if eff_id == EffectId.SCORE_UP:
            return SubType.SCORE_UP_PG if rare_0 == Rarity.SSR else SubType.SCORE_UP_P
        if eff_id == EffectId.PERFECTLIZE:
            return {
                Rarity.SSR: SubType.PERFECTLIZE_GGFS,
                Rarity.SR: SubType.PERFECTLIZE_GG,
                Rarity.R: SubType.PERFECTLIZE_G,
            }[rare_0]
        return SubType[eff_id.name]
    except KeyError as e:
        raise NotFoundError from e

def get_or_insert_card_entry(card, cursor, data, is_jp, name, name_1, rare_0, rare_1):
    res = []
    if is_jp:
        cursor.execute(get_card_info, (name))
        res = cursor.fetchall()
    else:
        if card['id'] < 9000:
            jp_name = ''
            for jp_card in data:
                if card['id'] == jp_card['id']:
                    jp_name = jp_card['name']
                    break
            jp_name = edit_name(jp_name)
            cursor.execute(get_card_info, (jp_name))
            res = cursor.fetchall()
        else:
            cursor.execute(get_card_info_as, (name))
            res = cursor.fetchall()

    # 新增卡片到資料庫
    if not res:
        idol_id = get_iid(name, cursor, is_jp)

        print('Inserting card', name)
        cursor.execute(config.ins_card if is_jp else config.ins_card_as, (name, idol_id, rare_0))
        cursor.connection.commit()
        print('Inserting card', name_1)
        cursor.execute(config.ins_card if is_jp else config.ins_card_as, (name_1, idol_id, rare_1))
        cursor.connection.commit()

        cursor.execute(get_card_info if is_jp else get_card_info_as, (name))
        res = cursor.fetchall()

    if not res:
        err = name + ' not found'
        errors.append(err)
        raise NotFoundError

    return res[0]

def handle_card(card, cursor, data, is_jp):
    global errors

    # 處理稀有度
    rare_0 = (card['rarity'] - 1) * 2
    rare_1 = rare_0 + 1

    # 在資料庫找到這張卡
    name = edit_name(card['name'])
    name_1 = name + '＋'
    print('Start', name)

    try:
        row = get_or_insert_card_entry(card, cursor, data, is_jp, name, name_1, rare_0, rare_1)
    except NotFoundError:
        return
    id_0 = row['id']
    id_1 = -1

    # 設定未覺醒和覺醒的配對
    if row['awaken'] is None:
        cursor.execute(get_card_info if is_jp else get_card_info_as, (name_1))
        res = cursor.fetchall()

        if not res:
            err = 'Awaken ' + name_1 + ' not found'
            errors.append(err)
            return

        id_1 = res[0]['id']
        print('Update awaken for', name)
        cursor.execute(config.set_card_awaken, (id_1, id_0))
        cursor.connection.commit()
        print('Update awaken for', name_1)
        cursor.execute(config.set_card_awaken, (id_0, id_1))
        cursor.connection.commit()
    else:
        id_1 = row['awaken']

    # 處理中文卡片名稱
    if not is_jp and row['as_name'] is None:
        print('Update as_name for', name)
        cursor.execute(config.set_card_cn_name, (name, id_0))
        print('Update as_name for', name_1)
        cursor.execute(config.set_card_cn_name, (name_1, id_1))
        cursor.connection.commit()

    # 處理沒有輸入偶像的情況
    if row['IID'] is None:
        idol_id = get_iid(name, cursor, is_jp)
        print('Set idol for', name)
        cursor.execute(config.set_card_iid, (idol_id, id_0))
        cursor.connection.commit()
        print('Set idol for', name_1)
        cursor.execute(config.set_card_iid, (idol_id, id_1))
        cursor.connection.commit()

    # 抓卡片實裝時間
    old_time = row['jp_time'] if is_jp else row['as_time']
    if old_time is None:
        url = os.path.join(config.card_info_root_url if is_jp else config.as_card_info_root_url, str(card['id']))
        span = config.bs4_data(url, 'span', class_='intl-date-dyts')
        if span:
            new_time = datetime.fromtimestamp(int(span[0]['data-date']) / 1000, timezone(timedelta(hours=9 if is_jp else 8)))

            print('Set new time', datetime.strftime(new_time, '%Y-%m-%card %H:%M:%S'), 'for', name)
            cursor.execute(config.set_card_time if is_jp else config.set_card_time_as, (new_time, id_0))
            cursor.connection.commit()
            print('Set new time', datetime.strftime(new_time, '%Y-%m-%card %H:%M:%S'), 'for', name_1)
            cursor.execute(config.set_card_time if is_jp else config.set_card_time_as, (new_time, id_1))
            cursor.connection.commit()
        else:
            err = 'No time for ' + name
            errors.append(err)


    # 處理 Center 效果
    if rare_0 != 0 and row['leader_skill'] is None:
        handle_l_skill(card['id'], id_0, id_1, name, name_1, is_jp, cursor)

    # 處理技能
    if rare_0 != 0:
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
                s_type = int(get_sub_type(skill['effectId'], rare_0))
            except NotFoundError:
                err = 'Error transposing skill type for ' + name
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
                    err = 'Fail to extract skill name for ' + name
                    errors.append(err)
            else:
                err = 'No skill name for ' + name
                errors.append(err)

            print('Set skill for', name)
            cursor.execute(config.set_card_skill if is_jp else config.set_card_skill_as, (s_type, s_name, json.dumps(s_val), id_0))
            print('Set skill for', name_1)
            cursor.execute(config.set_card_skill if is_jp else config.set_card_skill_as, (s_type, s_name, json.dumps(s_val), id_1))
            cursor.connection.commit()
        elif not is_jp and not row['as_skill_name']:
            s_name = ''
            url = os.path.join(config.as_card_info_root_url, str(card['id']))
            span = config.bs4_data(url, 'span', string='Skill')
            if span:
                has_sn, sn_str = config.consume(span[0].parent.text, 'Skill')
                if has_sn:
                    s_name = sn_str
                else:
                    err = 'Fail to extract skill name for ' + name
                    errors.append(err)
            else:
                err = 'No skill name for ' + name
                errors.append(err)

            print('Set skill cnname for', name)
            cursor.execute(config.set_card_skill_name_as, (s_name, id_0))
            print('Set skill cnname for', name_1)
            cursor.execute(config.set_card_skill_name_as, (s_name, id_1))
            cursor.connection.commit()

    # 處理取得方式等等
    if row['aquire'] is None:
        url = os.path.join(config.card_info_root_url if is_jp else config.as_card_info_root_url, str(card['id']))
        aquire, gashatype, ingasha = craw_aquire(url)
        print('Update aquire, gashatype, ingasha for', name)
        cursor.execute(config.set_card_aquire, (aquire, gashatype, ingasha, id_0))
        print('Update aquire, gashatype, ingasha for', name_1)
        cursor.execute(config.set_card_aquire, (5, gashatype, 2, id_1))
        cursor.connection.commit()

    # 處理卡片數值
    if row['visual_max'] is None:
        url = os.path.join(config.card_info_root_url if is_jp else config.as_card_info_root_url, str(card['id']))
        vals_0, vals_1 = craw_values(url, name, is_jp)
        if vals_0 is not None and vals_1 is not None:
            print('Update visual_max, vocal_max, dance_max for', name)
            cursor.execute(config.set_card_values, (vals_0['visual'], vals_0['vocal'], vals_0['dance'], id_0))
            print('Update visual_max, vocal_max, dance_max for', name_1)
            cursor.execute(config.set_card_values, (vals_1['visual'], vals_1['vocal'], vals_1['dance'], id_1))
            cursor.connection.commit()

    # 處理突破數值
    if row['visual_bonus'] is None or str(card['masterRankMax']) not in json.loads(row['visual_bonus']):
        master_rank = str(card['masterRankMax'])
        vi_bonus = {} if row['visual_bonus'] is None else json.loads(row['visual_bonus'])
        vo_bonus = {} if row['vocal_bonus'] is None else json.loads(row['vocal_bonus'])
        da_bonus = {} if row['dance_bonus'] is None else json.loads(row['dance_bonus'])
        vi_bonus[master_rank] = card['visualMasterBonus']
        vo_bonus[master_rank] = card['vocalMasterBonus']
        da_bonus[master_rank] = card['danceMasterBonus']
        print('Update value bonus for', name)
        cursor.execute(config.set_card_bonus, (json.dumps(vi_bonus), json.dumps(vo_bonus), json.dumps(da_bonus), id_0))
        print('Update value bonus for', name_1)
        cursor.execute(config.set_card_bonus, (json.dumps(vi_bonus), json.dumps(vo_bonus), json.dumps(da_bonus), id_1))
        cursor.connection.commit()

    # 處理最大突破
    if is_jp and row['jp_master_rank'] is None:
        print('Update max master rank for', name)
        cursor.execute(config.set_card_master, (card['masterRankMax'], id_0))
        print('Update max master rank for', name_1)
        cursor.execute(config.set_card_master, (card['masterRankMax'], id_1))
        cursor.connection.commit()
    elif not is_jp and row['as_master_rank'] is None:
        print('Update max master rank for', name)
        cursor.execute(config.set_card_master_as, (card['masterRankMax'], id_0))
        print('Update max master rank for', name_1)
        cursor.execute(config.set_card_master_as, (card['masterRankMax'], id_1))
        cursor.connection.commit()

    # 處理卡面文字
    if is_jp and row['jp_flavor'] is None:
        url = os.path.join(config.card_info_root_url, str(card['id']))
        flavor_0, flavor_1 = craw_flavor(url, name, is_jp)
        if flavor_0 is not None and flavor_1 is not None:
            print('Update flavor text for', name)
            cursor.execute(config.set_card_flavor, (flavor_0, id_0))
            print('Update flavor text for', name_1)
            cursor.execute(config.set_card_flavor, (flavor_1, id_1))
            cursor.connection.commit()
    elif not is_jp and row['as_flavor'] is None:
        url = os.path.join(config.as_card_info_root_url, str(card['id']))
        flavor_0, flavor_1 = craw_flavor(url, name, is_jp)
        if flavor_0 is not None and flavor_1 is not None:
            print('Update flavor text for', name)
            cursor.execute(config.set_card_flavor_as, (flavor_0, id_0))
            print('Update flavor text for', name_1)
            cursor.execute(config.set_card_flavor_as, (flavor_1, id_1))
            cursor.connection.commit()

    # 處理假 id
    if is_jp and row['card_id'] is None:
        cursor.execute(config.set_card_fake_id, (id_0-6, id_0))
        cursor.execute(config.set_card_fake_id, (id_1-6, id_1))
        cursor.connection.commit()

    # 爬 icon 圖
    icon_url_0 = os.path.join(config.icon_root_url, card['resourceId'] + '_0.png') if is_jp else os.path.join(config.as_icon_root_url, card['resourceId'] + '_0.png')
    icon_path_0 = os.path.join(config.icon_dir, str(id_0) + '.png')
    icon_url_1 = os.path.join(config.icon_root_url, card['resourceId'] + '_1.png') if is_jp else os.path.join(config.as_icon_root_url, card['resourceId'] + '_1.png')
    icon_path_1 = os.path.join(config.icon_dir, str(id_1) + '.png')

    craw_card('icon', name, icon_url_0, icon_path_0)
    craw_card('icon', name_1, icon_url_1, icon_path_1)

    # 爬卡面
    card_url_0 = os.path.join(config.card_root_url, card['resourceId'] + '_0_b.png') if is_jp else os.path.join(config.as_card_root_url, card['resourceId'] + '_0_b.png')
    card_path_0 = os.path.join(config.card_dir, str(id_0) + '.png')
    card_url_1 = os.path.join(config.card_root_url, card['resourceId'] + '_1_b.png') if is_jp else os.path.join(config.as_card_root_url, card['resourceId'] + '_1_b.png')
    card_path_1 = os.path.join(config.card_dir, str(id_1) + '.png')

    craw_card('card', name, card_url_0, card_path_0)
    craw_card('card', name_1, card_url_1, card_path_1)

    # 爬 SSR 大圖
    if rare_0 == 6:
        bg_url_0 = os.path.join(config.bg_root_url, card['resourceId'] + '_0.png') if is_jp else os.path.join(config.as_bg_root_url, card['resourceId'] + '_0.png')
        bg_path_0 = os.path.join(config.bg_dir, str(id_0) + '.png')
        bg_url_1 = os.path.join(config.bg_root_url, card['resourceId'] + '_1.png') if is_jp else os.path.join(config.as_bg_root_url, card['resourceId'] + '_1.png')
        bg_path_1 = os.path.join(config.bg_dir, str(id_1) + '.png')

        craw_card('bg', name, bg_url_0, bg_path_0)
        craw_card('bg', name_1, bg_url_1, bg_path_1)

    print('Finish card', name)

def main():
    global errors
    with open('cards.json') as f:
        data = json.load(f)

    with open('ascards.json') as f:
        cn_data = json.load(f)

    connection = config.connect()

    with connection.cursor() as cursor:
        cursor = DryCursor(cursor)

        # 更新 (日版) 卡片資訊
        for card in data:
            if card['extraType'] in [5, 7, 10] and card['rarity'] == 4:
                continue
            handle_card(card, cursor, data, True)

        # 更新 (海外版) 卡片資訊
        for card in cn_data:
            if card['extraType'] in [5, 7, 10] and card['rarity'] == 4:
                continue
            handle_card(card, cursor, data, False)

    connection.close()



    print('Errors:')
    for error in errors:
        print(error)


if __name__ == '__main__':
    main()
