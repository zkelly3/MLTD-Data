from config import connect

def main():
    data = []
    with open('ann_cards.txt') as f:
        line = f.readline()
        while line:
            data.append(line.strip().split(' '))
            line = f.readline()
    
    sel_card = "SELECT id FROM `Card` WHERE (jp_name = %s)"
    ins_ann2cd = "INSERT INTO `AnniversaryToCard` (`EID`, `CID`, `type`) VALUES(%s, %s, %s)"
    name_list = ['BRAND NEW PERFORMANCE', 'UNI-ONAIR', 'CHALLENGE FOR GLOW-RY DAYS']
    
    connection = connect()
    with connection.cursor() as cursor:
        cur = 0
        cnt = 0
        for d in data:
            ann_num = int(d[0])
            if ann_num != cur:
                cur = ann_num
                cnt = 0
            else:
                cnt += 1
            for i in range(1, len(d)):
                card_name = name_list[cur-1] + '　' + d[i]
                card_id = -1
                cursor.execute(sel_card, (card_name))
                res = cursor.fetchall()
                if res:
                    card_id = res[0]['id']
                print(cur, cnt, card_name, card_id)
                if card_id is not -1:
                    cursor.execute(ins_ann2cd, (cur, card_id, cnt))
                    connection.commit()
    connection.close()
    
if __name__ == '__main__':
    main()