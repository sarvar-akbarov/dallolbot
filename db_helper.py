import sqlite3
import time
import traceback


class DBHelper:

    def __init__(self):
        try:
            self.conn = sqlite3.connect('db/database.db')
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()

        except Exception as err:
            print(traceback.format_exc())

    def get_user(self, telegramid):
        user = self.conn.execute("SELECT * FROM users WHERE telegramid=:telegramid",
                                 {'telegramid': telegramid}).fetchone()
        if user:
            return user
        else:
            return False

    def insert(self, tableName, data):
        keys = data.keys()
        values = data.values()
        params = ["?" for i in range(len(data))]
        sql = "INSERT INTO {} ({}) VALUES ({})".format(tableName, ','.join(keys), ','.join(params))
        val = tuple(values)
        self.cursor.execute(sql, val)
        self.conn.commit()

    def update(self, tableName, id, data):
        keys = []
        values = []
        for key, value in data.items():
            keys.append(key + ' = ?')
            values.append(value)
        values.append(int(id))
        sql = "UPDATE " + tableName + " SET " + ','.join(keys) + " WHERE id = ?;"
        val = tuple(values)
        self.cursor.execute(sql, val)
        self.conn.commit()

    def user_save(self, user):
        user.update({'reg_date': time.time(), 'status': True, 'used_count': 0})
        keys = user.keys()
        values = user.values()
        params = ["?" for i in range(len(user))]
        sql = "INSERT INTO users ({}) VALUES ({})".format(','.join(keys), ','.join(params))
        val = tuple(values)
        self.cursor.execute(sql, val)
        self.conn.commit()

    def get_chats(self):
        sql = 'SELECT id,name,freelancer_id,client_id,is_admin,channel_link,status FROM chats WHERE status=1;'
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_chat(self, id):
        sql = "SELECT * FROM chats WHERE id = ? LIMIT 1;"
        self.cursor.execute(sql, (id,))
        chat = self.cursor.fetchone()
        if not chat:
            return False
        return chat

    def get_partner(self, telegramid):
        sql = "SELECT * FROM chats WHERE freelancer_id = ? AND status=1 LIMIT 1;"
        self.cursor.execute(sql, (telegramid,))
        chat = self.cursor.fetchone()
        print('chat', chat)

        if not chat:
            sql = "SELECT * FROM chats WHERE client_id = ? AND status=1 LIMIT 1;"
            self.cursor.execute(sql, (telegramid,))
            chat = self.cursor.fetchone()
            print('chat', chat)
            if not chat:
                return False
            return {'id': chat['freelancer_id'], 'link': chat['channel_link']}
        else:
            return {'id': chat['client_id'], 'link': chat['channel_link']}
