import sqlite3


class Database:
    def __init__(self, database):
        self.conn = sqlite3.connect(database, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS user (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             chat_id INTEGER NOT NULL,
             name TEXT NULL,
             contact TEXT NULL,
             birth TEXT NULL,
             region TEXT NULL,
             created_at DATETIME
            )
        """)
        self.conn.commit()

    def create_user(self, chat_id, created_at):
        self.cur.execute("""
            INSERT INTO user (chat_id, created_at) VALUES (?, ?)
        """, (chat_id, created_at)
                         )
        self.conn.commit()
    def check_user(self,chat_id):
        data = self.cur.execute("""
        SELECT * FROM user WHERE chat_id=?
        """,(chat_id,))
        return dict_fetchone(data)


    def get_user_by_chat_id(self, chat_id):
        self.cur.execute("""
            SELECT * FROM user WHERE chat_id = ?
        """, (chat_id,))
        user = dict_fetchone(self.cur)
        return user

    def update_user(self, state, chat_id, data):
        if state == 1:
            self.cur.execute("""
                UPDATE user SET name = ? WHERE chat_id = ?
            """, (data, chat_id)
                             )
        elif state == 2:
            self.cur.execute("""
                UPDATE user SET contact = ? WHERE chat_id = ?
            """, (data, chat_id)
                             )
        elif state == 3:
            self.cur.execute("""
                UPDATE user SET region = ? WHERE chat_id = ?
             """, (data, chat_id)
                             )
        elif state == 4:
            self.cur.execute("""
                UPDATE user SET contact = ? WHERE chat_id = ?
            """, (data, chat_id)
                             )
        self.conn.commit()

    def get_category_by_id_products(self, category_id, lang_id):
        if lang_id == 1:
            self.cur.execute("""
                 SELECT * FROM productuz WHERE category_id = ?
             """, (category_id,))
            products = dict_fetchall(self.cur)
            return products

        elif lang_id == 2:
            self.cur.execute("""
                 SELECT * FROM productru WHERE category_id = ?
             """, (category_id,))
            products = dict_fetchall(self.cur)
            return products

    def get_category_id_product(self, category_id, lang_id):
        print(lang_id)
        if lang_id == 1:
            self.cur.execute("""
                   SELECT * FROM productuz WHERE categoryuz_id = ?
               """, (category_id,))
            products = dict_fetchall(self.cur)
            return products
        elif lang_id == 2:
            self.cur.execute("""
                   SELECT * FROM productru WHERE categoryru_id = ?
               """, (category_id,))
            products = dict_fetchall(self.cur)
            return products

    def get_category(self, lang_id):
        if lang_id == 1:
            self.cur.execute("""
                SELECT * FROM categoryuz
            """)
            categories = dict_fetchall(self.cur)
            return categories

        elif lang_id == 2:
            self.cur.execute("""
               SELECT * FROM categoryru
            """)
            categories = dict_fetchall(self.cur)
            return categories

    def give_product(self, data, lang_id):
        if lang_id == 1:
            self.cur.execute("""
                SELECT * FROM productuz WHERE title = ?
            """, (data,))
            products = dict_fetchone(self.cur)
            return products
        elif lang_id == 2:
            self.cur.execute("""
                SELECT * FROM productru WHERE title = ?
            """, (data,))
            products = dict_fetchone(self.cur)
            return products

    def get_user_id(self, chat_id):
        self.cur.execute("""
                   SELECT id FROM user WHERE chat_id = ?
               """, (chat_id,))
        user_id = dict_fetchone(self.cur)
        return user_id

    def update_products(self, user_id, pk, name, lang_id):
        if lang_id == 1:
            self.cur.execute("""
                INSERT INTO info_productuz (user_id, product_id, title) VALUES (?, ?, ?)
            """, (user_id, pk, name))
            self.conn.commit()

        elif lang_id == 2:
            self.cur.execute("""
                            INSERT INTO info_productru (user_id, product_id, title) VALUES (?, ?, ?)
                        """, (user_id, pk, name))
            self.conn.commit()

    def get_product_id_max(self, user_id, lang_id):
        if lang_id == 1:
            self.cur.execute("""
                   SELECT MAX(id) FROM info_productuz WHERE user_id = ?
               """, (user_id,))
            id = dict_fetchone(self.cur)
            return id['MAX(id)']
        elif lang_id == 2:
            self.cur.execute("""
                          SELECT MAX(id) FROM info_productru WHERE user_id = ?
                      """, (user_id,))
            id = dict_fetchone(self.cur)
            return id['MAX(id)']

    def get_product_by_category_id(self, category_id, lang_id):
        if lang_id == 1:
            self.cur.execute("""
                      SELECT * FROM productuz WHERE categoryuz_id = ?
                  """, (category_id,))
            products = dict_fetchone(self.cur)
            return products['categoryuz_id']
        elif lang_id == 2:
            self.cur.execute("""
                              SELECT * FROM productru WHERE categoryru_id = ?
                          """, (category_id,))
            products = dict_fetchone(self.cur)
            return products['categoryru_id']

    def update_info_products(self, state, msg, info_id, lang_id):
        if lang_id == 1:
            if state == 6:
                self.cur.execute("""
                    UPDATE info_productuz SET price =? WHERE id = ?
                """, (msg, info_id))

            elif state == 7:
                self.cur.execute("""
                    UPDATE info_productuz set tons = ? where id = ?
                """, (msg, info_id))

            elif state == 8:
                self.cur.execute("""
                    UPDATE info_productuz SET city =? WHERE id = ?
               """, (msg, info_id))

            elif state == 9:
                self.cur.execute("""
                    UPDATE info_productuz SET customer =? WHERE id = ?
               """, (msg, info_id))

            elif state == 10:
                self.cur.execute("""
                    UPDATE info_productuz SET contact =? WHERE id = ?
               """, (msg, info_id))

            self.conn.commit()
        elif lang_id == 2:
            if state == 6:
                self.cur.execute("""
                    UPDATE info_productru SET price =? WHERE id = ?
                """, (msg, info_id))

            elif state == 7:
                self.cur.execute("""
                    UPDATE info_productru set tons = ? where id = ?
                """, (msg, info_id))

            elif state == 8:
                self.cur.execute("""
                    UPDATE info_productru SET city =? WHERE id = ?
               """, (msg, info_id))

            elif state == 9:
                self.cur.execute("""
                    UPDATE info_productru SET customer =? WHERE id = ?
               """, (msg, info_id))

            elif state == 10:
                self.cur.execute("""
                    UPDATE info_productru SET contact =? WHERE id = ?
               """, (msg, info_id))

            self.conn.commit()

    def give_info_product(self, pk, lang_id):
        if lang_id == 1:
            self.cur.execute("""
                SELECT * FROM info_productuz WHERE id = ?
            """, (pk,))
            infos = dict_fetchone(self.cur)
            return infos
        elif lang_id == 2:
            self.cur.execute("""
                 SELECT * FROM info_productru WHERE id = ?
             """, (pk,))
            infos = dict_fetchone(self.cur)
            return infos

    def get_info_product(self, title, lang_id):
        if lang_id == 1:
            self.cur.execute("""
             SELECT * FROM info_productuz WHERE title = ?
            """, (title,))
            info = dict_fetchall(self.cur)
            return info
        elif lang_id == 2:
            self.cur.execute("""
                        SELECT * FROM info_productru WHERE title = ?
                       """, (title,))
            info = dict_fetchall(self.cur)
            return info

    def get_product_id(self, title, lang_id):
        if lang_id == 1:
            self.cur.execute("""
                 SELECT categoryuz_id FROM productuz WHERE title = ?
             """, (title,))
            infos = dict_fetchone(self.cur)
            return infos['categoryuz_id']
        elif lang_id == 2:
            self.cur.execute("""
                             SELECT categoryru_id FROM productru WHERE title = ?
                         """, (title,))
            infos = dict_fetchone(self.cur)
            return infos['categoryru_id']


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))