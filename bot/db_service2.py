from db_service import Database

db = Database(
    host="localhost",
    user="root",
    password="Liverpool189256@",
    database="test",
    )

# for data in db.get_info_by_name_or_surname('test'):
#     txt = f'Имя: {data[0]}\nФамилия: {data[1]}\nОтчество: {data[2]}\nНомер телефона: {data[3]}\n'
#     print(txt)


db.search_info_by_full_name('test', 'testov', 'testovich')