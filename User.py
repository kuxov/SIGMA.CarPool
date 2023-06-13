import psycopg2


class DB:

    def __init__(self):
        self.conn = psycopg2.connect()
        self.cursor = self.conn.cursor()

    def user_init(self, usr, cht, tg):
        self.cursor.execute(
            "insert into users (id, chat_id, tgLink) values (" + str(usr) + ", " + str(cht) + ", '" + str(
                tg) + "')")
        self.conn.commit()
        self.cursor.execute(
            "insert into trip (user_id) values ('" + str(usr) + "')")
        self.conn.commit()

    def set_name(self, name, usr):
        self.cursor.execute("update users SET firstName = ('" + name + "') where id = " + str(usr))
        self.conn.commit()

    def set_phone(self, phone, usr):
        self.cursor.execute("update users set phone = ('" + phone + "') where id = " + str(usr))
        self.conn.commit()

    def set_metro(self, metro, usr):
        self.cursor.execute("update users set metro = '" + metro + "' where id = " + str(usr))
        self.conn.commit()

    def set_benefits(self, ben, usr):
        self.cursor.execute("update users set benefits = '" + str(ben) + "' where id = " + str(usr))
        self.conn.commit()

    def set_capacity(self, cap, usr):
        self.cursor.execute("update users set capacity = " + cap + " where id = " + str(usr))
        self.conn.commit()

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
        q = "update users set " + str(field) + "= '" + str(value) + "' where id = " + str(usr)
        data = (value, usr)
        self.cursor.execute(q, data)
        self.conn.commit()

        print(self.cursor.query)

    def set_trip_field(self, usr, value, field):
        q = "update trip set " + str(field) + " = '" + str(value) + "' where user_id = " + str(usr)
        data = (value, usr)
        self.cursor.execute(q, data)
        self.conn.commit()

        print(self.cursor.query)

    def get_date(self, usr):
        self.cursor.execute(
            'select trip_date from trip where user_id = ' + str(usr)
        )
        for row in self.cursor:
            return row

    def get_create_trip_info(self, usr):
        self.cursor.execute(
            'select trip_date, capacity, user_id, destination, metro from trip join users u on trip.user_id = u.id'
            ' where user_id = ' + str(usr)
        )

        for row in self.cursor:
            return row

    def get_find_trip_info(self, usr):
        self.cursor.execute(
            'select trip_date, user_id, destination, metro from trip join users u on trip.user_id = u.id'
            ' where user_id = ' + str(usr)
        )

        for row in self.cursor:
            return row
