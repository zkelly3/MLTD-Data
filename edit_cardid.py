import json
from config import connect
from fix_json import get_idol_names, handle_data

def main():
    idol_jp_names, idol_as_names = get_idol_names()
    
    with open('cards.json') as f:
        data = json.load(f)
        handle_data(data, idol_jp_names, 'jp')

    
    sql_set_cardid = "UPDATE `Card` SET card_id = %s WHERE (jp_name = %s)"
    connection = connect()
    with connection.cursor() as cursor:
        for card in data:
            print(card['name'])
            
            
            cursor.execute(sql_set_cardid, (card['id'], card['name']))
            cursor.execute(sql_set_cardid, (card['id'], card['name']+'＋'))
            connection.commit()
    connection.close()
    



if __name__ == '__main__':
    main()