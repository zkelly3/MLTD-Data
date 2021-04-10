import json
from config import connect

def handle_data(data, names, ver):
    for i in range(len(data)):
        name = data[i]['name']
        found = name in names
        half_idx = name.rfind(' ')
        full_idx = name.rfind('　')
        while half_idx is not -1 or full_idx is not -1:
            idx = max(half_idx, full_idx)
            if name[idx+1:] not in names:
                name = name[:idx] + name[idx+1:]
                half_idx = name.rfind(' ')
                full_idx = name.rfind('　')
            else:
                name = name[:idx] + '　' + name[idx+1:]
                found = True
                break

        data[i]['name'] = name
        if not found:
            print(ver, 'Error:', name)


def main():
    sql_get_all_idols = "SELECT * FROM `Idol`"

    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(sql_get_all_idols)
        idols = cursor.fetchall()
    connection.close()

    idol_jp_names = [idol['jp_name'] for idol in idols]
    for i in range(len(idol_jp_names)):
        if idol_jp_names[i] == 'エミリー スチュアート':
            idol_jp_names[i] = 'エミリー'
    idol_jp_names = [name for name in idol_jp_names if name is not None]

    idol_as_names = [idol['as_name'] for idol in idols]
    idol_as_names = [name for name in idol_as_names if name is not None]


    # 處理日版 json 資料
    with open('cards.json') as f:
        jp_data = json.load(f)

    handle_data(jp_data, idol_jp_names, 'jp')

    with open('cards.json', 'w') as f:
        json.dump(jp_data, f, ensure_ascii=False)

    # 處理海外版 json 資料
    with open('ascards.json') as f:
        as_data = json.load(f)

    handle_data(as_data, idol_as_names, 'as')

    with open('ascards.json', 'w') as f:
        json.dump(as_data, f, ensure_ascii=False)

if __name__ == '__main__':
    main()
