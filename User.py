from datetime import datetime

import psycopg2
import pytz
import gspread
from google.oauth2.service_account import Credentials
import json
import pandas as pd


client = gspread.authorize(creds)


class DB:

    def __init__(self):
        self.conn = psycopg2.connect()
        self.cursor = self.conn.cursor()

    def delete_user(self, usr):
        self.cursor.execute("delete from trip where user_id =" + str(usr))
        self.conn.commit()
        self.cursor.execute("delete from user where id =" + str(usr))
        self.conn.commit()

    def user_init(self, usr, cht, tg):

        curr = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')

        self.cursor.execute(
            "insert into users (id, chat_id, tgLink, registration_date, bonus) values (" + str(usr) + ", '" + str(
                cht) + "', '" + str(tg) + "', to_date('" + curr + "', 'YYYY-MM-DD'), 0)")
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

    def get_total_num(self):
        x = []

        self.cursor.execute(
            """
            select
  to_char(gen_month, 'Month YYYY'),
  count(id)
FROM generate_series(DATE '2023-01-01', current_date, INTERVAL '1' MONTH) m(gen_month)
LEFT OUTER JOIN users
ON ( date_trunc('month', registration_date) = date_trunc('month', gen_month) )
GROUP BY gen_month
Order by gen_month asc
            """
        )

        for row in self.cursor:
            x.append([row[0], row[1]])

        google_sh = client.open("SIGMA.CARPOOL")
        sheet1 = google_sh.get_worksheet(0)
        sheet1.clear()

        x.append(['____________', '____________'])
        self.cursor.execute('select count(id) from users')

        ttl = 0
        for row in self.cursor:
            ttl = row[0]

        x.append(["Total", ttl])

        sheet1.append_rows(values=x)


########################################################################################################################


if __name__ == '__main__':
    db = DB()
    print(db.get_total_num())
