from config import connect


def main():

    connection = connect()
    sql_select_idols = 'SELECT `id`, `jp_name`, `as_name` FROM `Idol` WHERE id <= 52'
    '''
    sql_insert_group = 'INSERT INTO `Group`(`jp_name`, `as_name`) VALUES(%s, %s)'
    sql_select_group = 'SELECT `id` FROM `Group` WHERE (`jp_name` = %s)'
    '''
    sql_insert_g2i = 'INSERT INTO `GroupToIdol`(`GID`, `IID`) VALUES(%s, %s)'

    with connection.cursor() as cursor:
        cursor.execute(sql_select_idols)
        idols = cursor.fetchall()
        for idol in idols:
            if not idol['jp_name'] == '田中琴葉':
                cursor.execute(sql_insert_g2i, (3, idol['id']))
                connection.commit()

    connection.close()


if __name__ == '__main__':
    main()