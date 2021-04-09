from datetime import datetime, timezone, timedelta
import json
import re
import os.path
from config import *

data = []
cn_data = []
errors = []

class FakeCursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, command, *args, **kwargs):
        if command.startswith("SELECT"):
            self.cursor.execute(command, *args, **kwargs)
        else:
            print (command, args, kwargs)

    def fetchall(self, *args, **kwargs):
        return self.cursor.fetchall(*args, **kwargs)

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
    
    cursor.execute(get_card_iid if is_jp else get_card_iid_as, (idol))
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
    span = bs4_data(url, string=re.compile('.*イベント:.*'))
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
    span = bs4_data(url, string=re.compile('.*ガシャ種別:.*'))
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
        spans = bs4_data(url, 'span', string=todo['target'])
        if len(spans) < 2:
            errors.append('Value ' + todo['target'] + ' for ' + name + ' not found')
            return None, None
        else:
            has_value, value = consume(spans[0].parent.text, todo['target'])
            if has_value:
                res_0[todo['key']] = int(value.split('(')[0].strip())
            else:
                res_0[todo['key']] = None
            has_value, value = consume(spans[1].parent.text, todo['target'])
            if has_value:
                res_1[todo['key']] = int(value.split('(')[0].strip())
            else:
                res_1[todo['key']] = None
    return res_0, res_1

def craw_flavor(url, name, is_jp):
    global errors
    target = 'フレーバーテキスト' if is_jp else 'Flavor text'
    spans = bs4_data(url, 'span', string=target)
    if len(spans) < 2:
        errors.append('Flavor Text for ' + name + ' not found')
        return None, None
    else:
        has_value, value = consume(spans[0].parent.text, target)
        res_0 = value if has_value else None
        has_value, value = consume(spans[1].parent.text, target)
        res_1 = value if has_value else None
    return res_0, res_1
    
def handle_card(d, cursor, connection, is_jp):
    global data, cn_data, errors
    
    # 處理稀有度
    rare_0 = (d['rarity'] - 1) * 2
    rare_1 = rare_0 + 1
    
    # 在資料庫找到這張卡
    guess = ['　', ' ']
    name = edit_name(d['name'])
    
    res = []
    if is_jp:
        cursor.execute(get_card_info, (name))
        res = cursor.fetchall()
    else:
        if d['id'] < 9000:
            jp_name = ''
            for jd in data:
                if d['id'] == jd['id']:
                    jp_name = jd['name']
                    break
            jp_name = edit_name(jp_name)
            cursor.execute(get_card_info, (jp_name))
            res = cursor.fetchall()
        else:
            cursor.execute(get_card_info_as, (name))
            res = cursor.fetchall()

    name_1 = name + '＋'
    print('Start', name)
    
    # 新增卡片到資料庫
    if not res:
        idol_id = get_iid(name, cursor, is_jp)
        
        print('Inserting card', name)
        cursor.execute(ins_card if is_jp else ins_card_as, (name, idol_id, rare_0))
        connection.commit()
        print('Inserting card', name_1)
        cursor.execute(ins_card if is_jp else ins_card_as, (name_1, idol_id, rare_1))
        connection.commit()
        
        cursor.execute(get_card_info if is_jp else get_card_info_as, (name))
        res = cursor.fetchall()
    
    if not res:
        err = name + ' not found'
        errors.append(err)
        return
    
    
    r = res[0]
    id_0 = r['id']
    id_1 = -1
    
    # 設定未覺醒和覺醒的配對
    if r['awaken'] is None:
        cursor.execute(get_card_info if is_jp else get_card_info_as, (name_1))
        res = cursor.fetchall()
        
        if not res:
            err = 'Awaken ' + name_1 + ' not found'
            errors.append(err)
            return
        
        id_1 = res[0]['id']
        print('Update awaken for', name)
        cursor.execute(set_card_awaken, (id_1, id_0))
        connection.commit()
        print('Update awaken for', name_1)
        cursor.execute(set_card_awaken, (id_0, id_1))
        connection.commit()
    else:
        id_1 = r['awaken']
    
    # 處理中文卡片名稱
    if not is_jp and r['as_name'] is None:
        print('Update as_name for', name)
        cursor.execute(set_card_cn_name, (name, id_0))
        print('Update as_name for', name_1)
        cursor.execute(set_card_cn_name, (name_1, id_1))
        connection.commit()
    
    # 處理沒有輸入偶像的情況
    if r['IID'] is None:
        idol_id = get_iid(name, cursor, is_jp)
        print('Set idol for', name)
        cursor.execute(set_card_iid, (idol_id, id_0))
        connection.commit()
        print('Set idol for', name_1)
        cursor.execute(set_card_iid, (idol_id, id_1))
        connection.commit()
    
    # 抓卡片實裝時間
    old_time = r['jp_time'] if is_jp else r['as_time']
    if old_time is None:
        url = os.path.join(card_info_root_url if is_jp else as_card_info_root_url, str(d['id']))
        span = bs4_data(url, 'span', class_='intl-date-dyts')
        if span:
            new_time = datetime.fromtimestamp(int(span[0]['data-date']) / 1000, timezone(timedelta(hours=9 if is_jp else 8)))
            
            print('Set new time', datetime.strftime(new_time, '%Y-%m-%d %H:%M:%S'), 'for', name)
            cursor.execute(set_card_time if is_jp else set_card_time_as, (new_time, id_0))
            connection.commit()
            print('Set new time', datetime.strftime(new_time, '%Y-%m-%d %H:%M:%S'), 'for', name_1)
            cursor.execute(set_card_time if is_jp else set_card_time_as, (new_time, id_1))
            connection.commit()
        else:
            err = 'No time for ' + name
            errors.append(err)
        
    
    # 處理 Center 效果
    if rare_0 != 0 and r['leader_skill'] is None:
        url = os.path.join(card_info_root_url if is_jp else as_card_info_root_url, str(d['id']))
        span = bs4_data(url, 'span', string='センター効果' if is_jp else 'Leader Skill')
        if span:
            has_ls, ls_str = consume(span[0].parent.text, 'センター効果' if is_jp else 'Leader Skill')
            if has_ls:
                if is_jp:
                    cursor.execute(get_card_lsid, (ls_str))
                else:
                    cursor.execute(get_card_lsid_as, (ls_str))
                res = cursor.fetchall()
                if res:
                    ls_id = res[0]['id']
                    print('Set leader skill for', name)
                    cursor.execute(set_card_lsid, (ls_id, id_0))
                    connection.commit()
                    print('Set leader skill for', name_1)
                    cursor.execute(set_card_lsid, (ls_id, id_1))
                    connection.commit()
                else:
                    err = 'Something wrong in leader skill string for ' + name
                    errors.append(err)
            else:
                err = 'Fail to extract leader skill for ' + name
                errors.append(err)
        else:
            err = 'No leader skill for ' + name
            errors.append(err)
    
    # 處理技能
    if rare_0 != 0:
        if r['skill_type'] is None:
            skill = d['skills'][0]
            s_val = {
                'cd': skill['interval'],
                'prob': skill['probability'],
                'dur': skill['duration'],
                'val': []
            }
            for v in skill['value']:
                s_val['val'].append(v)
            
            eff_id = skill['effectId']
            s_type = -1
            if eff_id == 1:
                if rare_0 == 6:
                    s_type = 1
                else:
                    s_type = 2
            elif eff_id == 2:
                s_type = 3
            elif eff_id == 3:
                s_type = 4
            elif eff_id == 4:
                s_type = 5
            elif eff_id == 5:
                s_type = 6
            elif eff_id == 6:
                if rare_0 == 6:
                    s_type = 7
                elif rare_0 == 4:
                    s_type = 8
                elif rare_0 == 2:
                    s_type = 9
            elif eff_id == 7:
                s_type = 10
            elif eff_id == 8:
                s_type = 11
            elif eff_id == 10:
                s_type = 12
            elif eff_id == 11:
                s_type = 13
            
            if s_type == -1:
                err = 'Error transposing skill type for ' + name
                errors.append(err)
            
            s_name = ''
            url = os.path.join(card_info_root_url if is_jp else as_card_info_root_url, str(d['id']))
            span = bs4_data(url, 'span', string='スキル' if is_jp else 'Skill')
            if span:
                has_sn, sn_str = consume(span[0].parent.text, 'スキル' if is_jp else 'Skill')
                if has_sn:
                    s_name = sn_str
                else:
                    err = 'Fail to extract skill name for ' + name
                    errors.append(err)
            else:
                err = 'No skill name for ' + name
                errors.append(err)
            
            print('Set skill for', name)    
            cursor.execute(set_card_skill if is_jp else set_card_skill_as, (s_type, s_name, json.dumps(s_val), id_0))
            print('Set skill for', name_1)
            cursor.execute(set_card_skill if is_jp else set_card_skill_as, (s_type, s_name, json.dumps(s_val), id_1))
            connection.commit()
        elif not is_jp and not r['as_skill_name']:
            s_name = ''
            url = os.path.join(as_card_info_root_url, str(d['id']))
            span = bs4_data(url, 'span', string='Skill')
            if span:
                has_sn, sn_str = consume(span[0].parent.text, 'Skill')
                if has_sn:
                    s_name = sn_str
                else:
                    err = 'Fail to extract skill name for ' + name
                    errors.append(err)
            else:
                err = 'No skill name for ' + name
                errors.append(err)
            
            print('Set skill cnname for', name)    
            cursor.execute(set_card_skill_name_as, (s_name, id_0))
            print('Set skill cnname for', name_1)
            cursor.execute(set_card_skill_name_as, (s_name, id_1))
            connection.commit()        
    
    # 處理取得方式等等
    if r['aquire'] is None:
        url = os.path.join(card_info_root_url if is_jp else as_card_info_root_url, str(d['id']))
        aquire, gashatype, ingasha = craw_aquire(url)
        print('Update aquire, gashatype, ingasha for', name)
        cursor.execute(set_card_aquire, (aquire, gashatype, ingasha, id_0))
        print('Update aquire, gashatype, ingasha for', name_1)
        cursor.execute(set_card_aquire, (5, gashatype, 2, id_1))
        connection.commit()
    
    # 處理卡片數值
    if r['visual_max'] is None:
        url = os.path.join(card_info_root_url if is_jp else as_card_info_root_url, str(d['id']))
        vals_0, vals_1 = craw_values(url, name, is_jp)
        if vals_0 is not None and vals_1 is not None:
            print('Update visual_max, vocal_max, dance_max for', name)
            cursor.execute(set_card_values, (vals_0['visual'], vals_0['vocal'], vals_0['dance'], id_0))
            print('Update visual_max, vocal_max, dance_max for', name_1)
            cursor.execute(set_card_values, (vals_1['visual'], vals_1['vocal'], vals_1['dance'], id_1))
            connection.commit()
    
    # 處理突破數值
    if r['visual_bonus'] is None or str(d['masterRankMax']) not in json.loads(r['visual_bonus']):
        master_rank = str(d['masterRankMax'])
        vi_bonus = {} if r['visual_bonus'] is None else json.loads(r['visual_bonus'])
        vo_bonus = {} if r['vocal_bonus'] is None else json.loads(r['vocal_bonus'])
        da_bonus = {} if r['dance_bonus'] is None else json.loads(r['dance_bonus'])
        vi_bonus[master_rank] = d['visualMasterBonus']
        vo_bonus[master_rank] = d['vocalMasterBonus']
        da_bonus[master_rank] = d['danceMasterBonus']
        print('Update value bonus for', name)
        cursor.execute(set_card_bonus, (json.dumps(vi_bonus), json.dumps(vo_bonus), json.dumps(da_bonus), id_0))
        print('Update value bonus for', name_1)
        cursor.execute(set_card_bonus, (json.dumps(vi_bonus), json.dumps(vo_bonus), json.dumps(da_bonus), id_1))
        connection.commit()
    
    # 處理最大突破
    if is_jp and r['jp_master_rank'] is None:
        print('Update max master rank for', name)
        cursor.execute(set_card_master, (d['masterRankMax'], id_0))
        print('Update max master rank for', name_1)
        cursor.execute(set_card_master, (d['masterRankMax'], id_1))
        connection.commit()
    elif not is_jp and r['as_master_rank'] is None:
        print('Update max master rank for', name)
        cursor.execute(set_card_master_as, (d['masterRankMax'], id_0))
        print('Update max master rank for', name_1)
        cursor.execute(set_card_master_as, (d['masterRankMax'], id_1))
        connection.commit()
    
    # 處理卡面文字
    if is_jp and r['jp_flavor'] is None:
        url = os.path.join(card_info_root_url, str(d['id']))
        flavor_0, flavor_1 = craw_flavor(url, name, is_jp)
        if flavor_0 is not None and flavor_1 is not None:
            print('Update flavor text for', name)
            cursor.execute(set_card_flavor, (flavor_0, id_0))
            print('Update flavor text for', name_1)
            cursor.execute(set_card_flavor, (flavor_1, id_1))
            connection.commit()
    elif not is_jp and r['as_flavor'] is None:
        url = os.path.join(as_card_info_root_url, str(d['id']))
        flavor_0, flavor_1 = craw_flavor(url, name, is_jp)
        if flavor_0 is not None and flavor_1 is not None:
            print('Update flavor text for', name)
            cursor.execute(set_card_flavor_as, (flavor_0, id_0))
            print('Update flavor text for', name_1)
            cursor.execute(set_card_flavor_as, (flavor_1, id_1))
            connection.commit()
    
    # 處理假 id
    if is_jp and r['card_id'] is None:
        cursor.execute(set_card_fake_id, (id_0-6, id_0))
        cursor.execute(set_card_fake_id, (id_1-6, id_1))
        connection.commit()
    
    # 爬 icon 圖
    icon_url_0 = os.path.join(icon_root_url, d['resourceId'] + '_0.png') if is_jp else os.path.join(as_icon_root_url, d['resourceId'] + '_0.png')
    icon_path_0 = os.path.join(icon_dir, str(id_0) + '.png')
    icon_url_1 = os.path.join(icon_root_url, d['resourceId'] + '_1.png') if is_jp else os.path.join(as_icon_root_url, d['resourceId'] + '_1.png')
    icon_path_1 = os.path.join(icon_dir, str(id_1) + '.png')
    
    craw_card('icon', name, icon_url_0, icon_path_0)
    craw_card('icon', name_1, icon_url_1, icon_path_1)
    
    # 爬卡面
    card_url_0 = os.path.join(card_root_url, d['resourceId'] + '_0_b.png') if is_jp else os.path.join(as_card_root_url, d['resourceId'] + '_0_b.png')
    card_path_0 = os.path.join(card_dir, str(id_0) + '.png')
    card_url_1 = os.path.join(card_root_url, d['resourceId'] + '_1_b.png') if is_jp else os.path.join(as_card_root_url, d['resourceId'] + '_1_b.png')
    card_path_1 = os.path.join(card_dir, str(id_1) + '.png')
    
    craw_card('card', name, card_url_0, card_path_0)
    craw_card('card', name_1, card_url_1, card_path_1)
    
    # 爬 SSR 大圖
    if rare_0 == 6:
        bg_url_0 = os.path.join(bg_root_url, d['resourceId'] + '_0.png') if is_jp else os.path.join(as_bg_root_url, d['resourceId'] + '_0.png')
        bg_path_0 = os.path.join(bg_dir, str(id_0) + '.png')
        bg_url_1 = os.path.join(bg_root_url, d['resourceId'] + '_1.png') if is_jp else os.path.join(as_bg_root_url, d['resourceId'] + '_1.png')
        bg_path_1 = os.path.join(bg_dir, str(id_1) + '.png')
        
        craw_card('bg', name, bg_url_0, bg_path_0)
        craw_card('bg', name_1, bg_url_1, bg_path_1)
    
    print('Finish card', name)        

def main():
    global data, cn_data, errors
    with open('cards.json') as f:
        data = json.load(f)
    
    with open('cncards.json') as f:
        cn_data = json.load(f)
    
    connection = connect()
    
    with connection.cursor() as cursor:
        cursor = FakeCursor(cursor)

        # 更新 (日版) 卡片資訊
        for d in data:
            if d['extraType'] in [5, 7, 10] and d['rarity'] == 4:
                continue
            handle_card(d, cursor, connection, True)
        
        # 更新 (海外版) 卡片資訊
        for d in cn_data:
            if d['extraType'] in [5, 7, 10] and d['rarity'] == 4:
                continue
            handle_card(d, cursor, connection, False)
    
    connection.close()
    
    
    
    print('Errors:')
    for error in errors:
        print(error)
        

if __name__ == '__main__':
    main()
