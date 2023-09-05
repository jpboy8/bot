import mysql.connector
from mysql.connector import pooling

class Database:
    def __init__(self, host, user, password, database):
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name='mypool', 
                                                                           pool_size=20, 
                                                                           pool_reset_session=True, 
                                                                           host=host, user=user, password=password, 
                                                                           database=database)

    
    def add_user(self, user_id, name, surname, phone_number):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO users (user_id, name, surname, phone_number) VALUES (%s, %s, %s, %s)", (user_id, name, surname, phone_number))
                conn.commit()


    def user_exists(self, user_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM users WHERE user_id = %s", (user_id, ))
                if len(cursor.fetchall()) != 0:
                    return True
                else:
                    return False
                
    
    def set_name(self, user_id, name):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET name = %s WHERE user_id = %s", (name.capitalize(), user_id))
                conn.commit()

    def set_surname(self, user_id, surname):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET surname = %s WHERE user_id = %s", (surname.capitalize(), user_id))
                conn.commit()

    def set_phone_number(self, user_id, phone_number):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET phone_number = %s WHERE user_id = %s", (phone_number, user_id))
                conn.commit()

    def show_profile(self, user_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name, surname, phone_number FROM users WHERE user_id = %s", (user_id, ))
                result = cursor.fetchall()
                name = result[0][0]
                surname = result[0][1]
                phone = result[0][2]

                return f'Имя: {name}\nФамилия: {surname}\nНомер телефона: {phone}'
    

    # Для Админов
    # Добавление чата в бд
    def add_chat(self, chat_id, title):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO chats (chat_id, name) VALUES (%s, %s)", (chat_id, title))
                conn.commit()
    
    # Проверка на существование чата в бд
    def chat_exists(self, chat_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM chats WHERE chat_id = %s", (chat_id, ))
                if len(cursor.fetchall()) != 0:
                    return True
                else:
                    return False
    
    # Добавление записей в таблицу chat_members
    def add_chat_member(self, user_id, chat_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM chats WHERE chat_id = %s", (chat_id, ))
                if len(cursor.fetchall()) != 0:
                    cursor.execute("SELECT name FROM users WHERE user_id = %s", (user_id, ))
                    if len(cursor.fetchall()) != 0:
                        cursor.execute("SELECT id FROM chat_members WHERE user_id = %s AND chat_id = %s", (user_id, chat_id))
                        if len(cursor.fetchall()) == 0:
                            cursor.execute("INSERT INTO chat_members (user_id, chat_id) VALUES (%s, %s)", (user_id, chat_id))
                            conn.commit()


# находит инфу об юзере по имени и фамилии
    def search_info_by_name_and_surname(self, name, surname):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id, phone_number from users WHERE name = %s AND surname = %s", (name, surname))
                user_info = cursor.fetchone()
                user_id = user_info[0]
                u_phone_number = user_info[1]

                cursor.execute(
                    """
                    SELECT
                        chats.name
                    FROM users
                    INNER JOIN chat_members ON users.user_id = chat_members.user_id
                    INNER JOIN chats ON chat_members.chat_id = chats.chat_id
                    WHERE users.user_id = %s;
                    """,
                    (user_id, ))
                
                groups = cursor.fetchall()
                
                dict_info = {
                    'name': name,
                    'surname': surname,
                    'phone': u_phone_number,
                    'groups': groups
                }

                return dict_info


# находит инфу об юзере по номеру телефона
    def search_info_by_phone(self, phone):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id, name, surname from users WHERE phone_number = %s", (phone, ))
                user_info = cursor.fetchone()
                user_id = user_info[0]
                u_name = user_info[1]
                u_surname = user_info[2]

                cursor.execute(
                    """
                    SELECT
                        chats.name
                    FROM users
                    INNER JOIN chat_members ON users.user_id = chat_members.user_id
                    INNER JOIN chats ON chat_members.chat_id = chats.chat_id
                    WHERE users.user_id = %s;
                    """,
                    (user_id, ))
                
                groups = cursor.fetchall()
                
                dict_info = {
                    'name': u_name,
                    'surname': u_surname,
                    'phone': phone,
                    'groups': groups
                }

                return dict_info


# удаление по юзер айди
    def delete_from_bd(self, user_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id, ))
                conn.commit()
                 

 # находит айди юзера и все группы в которых он состоит   
    def get_user_id_and_groups_by_phone(self, phone):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                 cursor.execute("SELECT user_id FROM users WHERE phone_number = %s", (phone, ))
                 user_id = cursor.fetchone()[0]

                 cursor.execute(
                    """
                    SELECT
                        chats.name,
                        chats.chat_id
                    FROM users
                    INNER JOIN chat_members ON users.user_id = chat_members.user_id
                    INNER JOIN chats ON chat_members.chat_id = chats.chat_id
                    WHERE users.user_id = %s;
                    """,
                    (user_id, ))
                 
                 groups = cursor.fetchall()

                 dict_info = {
                    'user_id': user_id,
                    'phone': phone,
                    'groups': groups
                 }

                 return dict_info
            
                
                

db = Database(
    host="localhost",
    user="root",
    password="Liverpool189256@",
    database="test",
    )

db.search_info_by_phone('=235')