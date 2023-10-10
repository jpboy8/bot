import mysql.connector
from mysql.connector import pooling
from mysql.connector.errors import PoolError

from utils import repeat_if_failed


class Database:
    def __init__(self, host, user, password, database):
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=20,
            pool_reset_session=True,
            host=host,
            user=user,
            password=password,
            database=database,
        )

    # 
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def add_user(self, user_id, name, surname, phone_number, patronymic):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (user_id, name, surname, phone_number, patronymic) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, name, surname, phone_number, patronymic),
                )
                conn.commit()

    # 
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def user_exists(self, user_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM users WHERE user_id = %s", (user_id,))
                if len(cursor.fetchall()) != 0:
                    return True
                else:
                    return False

    # 
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def set_name(self, user_id, name):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET name = %s WHERE user_id = %s",
                    (name.capitalize(), user_id),
                )
                conn.commit()

    # 
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def set_surname(self, user_id, surname):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET surname = %s WHERE user_id = %s",
                    (surname.capitalize(), user_id),
                )
                conn.commit()

    # 
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def set_phone_number(self, user_id, phone_number):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET phone_number = %s WHERE user_id = %s",
                    (phone_number, user_id),
                )
                conn.commit()

    # 
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))            
    def set_patronymic(self, user_id, patronymic):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET patronymic = %s WHERE user_id = %s",
                    (patronymic.capitalize(), user_id),
                )
                conn.commit()

    # 
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def show_profile(self, user_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT name, surname, phone_number, patronymic FROM users WHERE user_id = %s",
                    (user_id,),
                )
                result = cursor.fetchall()
                name = result[0][0]
                surname = result[0][1]
                phone = result[0][2]
                patronymic = result[0][3]

                return f"Имя: {name}\nФамилия: {surname}\nОтчество: {patronymic}\nНомер телефона: {phone}"

    # Для Админов
    # Добавление чата в бд
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def add_chat(self, chat_id, title):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO chats (chat_id, name) VALUES (%s, %s)",
                    (chat_id, title),
                )
                conn.commit()

    # Проверка на существование чата в бд
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def chat_exists(self, chat_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM chats WHERE chat_id = %s", (chat_id,))
                if len(cursor.fetchall()) != 0:
                    return True
                else:
                    return False
                
    # Проверка на существования номер телефона в бд
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def phone_exists(self, phone):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM users WHERE phone_number = %s", (phone,))
                if len(cursor.fetchall()) != 0:
                    return True
                else:
                    return False

    # Добавление записей в таблицу chat_members
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def add_chat_member(self, user_id, chat_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM chats WHERE chat_id = %s", (chat_id,))
                if len(cursor.fetchall()) != 0:
                    cursor.execute(
                        "SELECT name FROM users WHERE user_id = %s", (user_id,)
                    )
                    if len(cursor.fetchall()) != 0:
                        cursor.execute(
                            "SELECT id FROM chat_members WHERE user_id = %s AND chat_id = %s",
                            (user_id, chat_id),
                        )
                        if len(cursor.fetchall()) == 0:
                            cursor.execute(
                                "INSERT INTO chat_members (user_id, chat_id) VALUES (%s, %s)",
                                (user_id, chat_id),
                            )
                            conn.commit()

    # находит инфу об юзере по фио
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def search_info_by_full_name(self, name, surname, patronymic):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                SELECT u.name, u.surname, u.phone_number, u.patronymic, 
                IFNULL(GROUP_CONCAT(c.name), 'Нет групп') AS group_names
                FROM users u
                LEFT JOIN chat_members cm ON u.user_id = cm.user_id
                LEFT JOIN chats c ON cm.chat_id = c.chat_id
                WHERE u.name = %s AND u.surname = %s AND u.patronymic = %s
                GROUP BY u.user_id;
                """, (name, surname, patronymic))

                for data in cursor.fetchall():
                    yield data

                

    # находит инфу об юзере по номеру телефона
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def search_info_by_phone(self, phone):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT u.name, u.surname, u.phone_number, u.patronymic, 
                        IFNULL(GROUP_CONCAT(c.name), 'Нет групп') AS group_names
                    FROM users u
                    LEFT JOIN chat_members cm ON u.user_id = cm.user_id
                    LEFT JOIN chats c ON cm.chat_id = c.chat_id
                    WHERE u.phone_number = %s
                    GROUP BY u.user_id;
                    """, (phone, )
                )

                for data in cursor.fetchall():
                    yield data
               

    # удаление по юзер айди
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def delete_from_bd(self, user_id):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                conn.commit()

    # находит айди юзера и все группы в которых он состоит
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def get_user_id_and_groups_by_phone(self, phone):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT user_id FROM users WHERE phone_number = %s", (phone,)
                )
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
                    (user_id,),
                )

                groups = cursor.fetchall()

                dict_info = {"user_id": user_id, "phone": phone, "groups": groups}

                return dict_info
    

    # дает инфу об юзере либо по имени либо по фамилии либо по номеру телефона
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def get_info_by_name_or_surname(self, data):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name, surname, patronymic, phone_number FROM users where name = %s OR surname = %s OR phone_number = %s", (data.capitalize(), data.capitalize(), data.capitalize()))
                for row in cursor.fetchall():
                    yield row


    # возвращает инфу о юзере по имени и фамилии
    @repeat_if_failed(count=2, handled_exceptions=(PoolError,))
    def get_info_by_name_and_surname(self, name, surname):
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                SELECT u.name, u.surname, u.phone_number, u.patronymic, 
                IFNULL(GROUP_CONCAT(c.name), 'Нет групп') AS group_names
                FROM users u
                LEFT JOIN chat_members cm ON u.user_id = cm.user_id
                LEFT JOIN chats c ON cm.chat_id = c.chat_id
                WHERE u.name = %s AND u.surname = %s
                GROUP BY u.user_id;
                """, (name, surname, ))

                for row in cursor.fetchall():
                    yield row
                    

# db = Database(
#     host="localhost",
#     user="root",
#     password="Liverpool189256@",
#     database="test",
#     )

# for i in range(10):
#     db.add_user(1243465+i, 'Test', 'Testov', 12435+i, 'Testovich')