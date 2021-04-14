class NotFoundError(Exception):
    pass

class Database:
    def __init__(self, cursor, is_jp):
        self.cursor = cursor
        self.scope = ''
        self.is_jp = is_jp
        if is_jp:
            self.col_mapping = {
                'name': 'jp_name',
                'time': 'jp_time',
                'start': 'jp_start',
                'over': 'jp_over',
                'description': 'jp_description',
                'skill_name': 'jp_skill_name',
                'master_rank': 'jp_master_rank',
                'flavor': 'jp_flavor',
            }
        else:
            self.col_mapping = {
                'name': 'as_name',
                'time': 'as_time',
                'start': 'as_start',
                'over': 'as_over',
                'description': 'as_description',
                'skill_name': 'as_skill_name',
                'master_rank': 'as_master_rank',
                'flavor': 'as_flavor',
            }

    def map_column(self, column):
        if column in self.col_mapping:
            return self.col_mapping[column]
        return column

    @staticmethod
    def parse_conditions(conds):
        template = ' AND '.join(['{0} = %s'.format(key) for key in conds.keys()])
        return template, tuple(conds.values())

    @staticmethod
    def parse_columns(columns):
        template = ', '.join(['{0} = %s'.format(key) for key in columns.keys()])
        return template, tuple(columns.values())

    def fetch_one(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)
        res = self.cursor.fetchall()
        if not res:
            raise NotFoundError
        return res[0]

    def edit_database(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)
        self.cursor.connection.commit()

    def select_row(self, table_name, columns, conds):
        columns = [self.map_column(col) for col in columns]
        conds = {self.map_column(k): v for (k, v) in conds.items()}
        template, values = self.parse_conditions(conds)
        return self.fetch_one('SELECT {columns} FROM `{table_name}` WHERE ({template})'.format(
            columns=', '.join(columns), table_name=table_name, template=template), values)

    def update_row(self, table_name, columns, conds):
        columns = {self.map_column(k): v for (k, v) in columns.items()}
        conds = {self.map_column(k): v for (k, v) in conds.items()}
        col_template, col_values = self.parse_columns(columns)
        cond_template, cond_values = self.parse_conditions(conds)
        values = col_values + cond_values
        self.edit_database('UPDATE `{table_name}` SET {col_template} WHERE ({cond_template})'.format(
            table_name=table_name, col_template=col_template, cond_template=cond_template), values)

    def insert_row(self, table_name, columns):
        columns = {self.map_column(k): v for (k, v) in columns.items()}
        self.edit_database('INSERT INTO `{table_name}`({key_template}) VALUES({value_template})'.format(
            table_name=table_name, key_template=', '.join(columns.keys()), value_template=', '.join(['%s'] * len(columns))), tuple(columns.values()))

    def get_card_info(self, **conds):
        return self.select_row('Card', ['*'], conds)

    def get_card_iid(self, **conds):
        return self.select_row('Idol', ['id'], conds)['id']

    def get_card_lskill_id(self, **conds):
        return self.select_row('LeaderSkill', ['id'], conds)['id']

    def insert_card(self, **columns):
        self.insert_row('Card', columns)

    def update_card(self, info, **columns):
        print('update {col} for {name}'.format(col=', '.join(columns.keys()), name=info.name))
        return self.update_row('Card', columns, {'id': info.id})

    def update_cards(self, infos, **columns):
        for info in infos:
            self.update_card(info, **columns)