import psycopg2


class DB:

    def __init__(self):
        self.cursor = self.conn.cursor()

    def user_init(self, usr, cht, tg):
        self.cursor.execute(
            'insert into users (id, chat_id, tgLink) values (' + str(usr) + ', ' + str(cht) + ', ' + str(
                tg) + ')')

    def set_name(self, name, usr):
        self.cursor.execute('insert into users (firstName) values (' + name + ') where id = ' + str(usr) + '')

    def set_phone(self, phone, usr):
        self.cursor.execute('insert into users (phone) values (' + str(phone) + ') where id = ' + str(usr) + '')

    def set_metro(self, metro, usr):
        self.cursor.execute('insert into users (metro) values (' + metro + ') where id = ' + str(usr) + '')

    def set_benefits(self, ben, usr):
        self.cursor.execute('insert into users (benefits) values (' + ben + ') where id = ' + str(usr) + '')

    def set_capacity(self, cap, usr):
        self.cursor.execute('insert into users (capacity) values (' + cap + ') where id = ' + str(usr) + '')

    def get_driver_r(self, usr):
        self.cursor.execute(
            'select id, firstName, phone, tgLink, capacity, metro from users where id = ' + str(usr))
        for row in self.cursor:
            return row

    def get_passenger_r(self, usr):
        self.cursor.execute(
            'select id, firstName, phone, tgLink, benefits, metro from users where id = ' + str(usr))
        for row in self.cursor:
            return row

    def update_field(self, usr, value, field):

        q = """update users set firstname = %s where id = %s"""
        q = "update users set " + str(field) + "= '" + str(value) + "' where id = " + str(usr)
        data = (value, usr)
        self.cursor.execute(q, data)
        self.conn.commit()

        print(self.cursor.query)
