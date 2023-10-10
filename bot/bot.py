import re
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db_service import Database
from user_reg import UserReg

import os
from dotenv import load_dotenv

load_dotenv()

db = Database(
    host=os.getenv('host'),
    user=os.getenv("user"),
    password=os.getenv('password'),
    database=os.getenv('database'),
    )

storage = MemoryStorage()
bot = Bot(token="6441552887:AAEstnF_R31pkqxdwT0Rgmu3ffvIAAMkBYU")
dp = Dispatcher(bot, storage=storage)
adm_chat_id = -1001943857518

inkb = InlineKeyboardMarkup(row_width=1)

profile_btn = InlineKeyboardButton(text="Профиль", callback_data='show_profile')
change_name_btn = InlineKeyboardButton(text="Изменить имя", callback_data='change_name')
change_surname_btn = InlineKeyboardButton(text="Изменить фамилию", callback_data='change_surname')
change_patronymic_btn = InlineKeyboardButton(text="Изменить отчество", callback_data='change_patronymic')
change_phone_number_btn = InlineKeyboardButton(text="Изменить номер телефона", callback_data='change_phone_number')
register_btn = InlineKeyboardButton(text="Регистрация", callback_data='reg')

inkb.add(profile_btn, change_name_btn, change_surname_btn, change_patronymic_btn, change_phone_number_btn, register_btn)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.from_user.id, 'Введите /commands для просмотра всех функций бота.\nЕсли вы еще не регистрировались, то сначала нажмите на кнопку "Регистрация"')


# Выводит список команд
@dp.message_handler(commands=['commands'])
async def show_functions(message: types.Message):
    if message.chat.type == 'private':
        await message.answer('Cписок команд', reply_markup=inkb)


# Ловит стейт на изменение номера телефона
@dp.message_handler(state=UserReg.change_phone)
async def handle_change_phone_number_message(message: types.Message,state=FSMContext):
    pattern = "^\\+?[1-9][0-9]{7,14}$"

    phone_number = message.text

    if re.match(pattern, phone_number) is not None:
        db.set_phone_number(message.from_user.id, phone_number)
        await state.finish()
        bot.send_message(message.from_user.id, 'Вы успешно изменили номер телефона!')
    else:
        bot.send_message(message.from_user.id, 'Номера телефона не соответствует формату')



# Отслеживает нажатие на кнопку "изменить номер телефона"
@dp.callback_query_handler(text='change_phone_number')
async def change_phone_nub_btn(callback: types.CallbackQuery):
    if not db.user_exists(callback.from_user.id):
        await bot.send_message(callback.from_user.id, 'Вы еще не зарегистрировались!')
        await callback.answer()
    else:
        await bot.send_message(callback.from_user.id, 'Введите ваш номер телефона с кодом страны и без пробелов. Пример для заполнения: +77017299556 ')
        await UserReg.change_phone.set() 
        await callback.answer()


# Отслеживает нажатие на кнопку "изменить отчество"
@dp.callback_query_handler(text='change_patronymic')
async def change_patronymic_btn(callback: types.CallbackQuery):
    if not db.user_exists(callback.from_user.id):
        await bot.send_message(callback.from_user.id, 'Вы еще не зарегистрировались!')
        await callback.answer()
    else:
        await bot.send_message(callback.from_user.id, 'Введите отчество на кириллице: ')
        await UserReg.change_patronymic.set()
        await callback.answer()


# Ловит стейт на изменение отчества
@dp.message_handler(state=UserReg.change_patronymic)
async def handle_change_surname_message(message: types.Message,state=FSMContext):
    db.set_patronymic(message.from_user.id, message.text)
    await state.finish()
    await bot.send_message(message.from_user.id, 'Вы успешно изменили отчество!')


# Отслеживает нажатие на кнопку "изменить фамилию"
@dp.callback_query_handler(text='change_surname')
async def change_surname_btn(callback: types.CallbackQuery):
    if not db.user_exists(callback.from_user.id):
        await bot.send_message(callback.from_user.id, 'Вы еще не зарегистрировались!')
        await callback.answer()
    else:
        await bot.send_message(callback.from_user.id, 'Введите фамилию на кириллице: ')
        await UserReg.change_surname.set()
        await callback.answer()


# Ловит стейт на изменение фамилии
@dp.message_handler(state=UserReg.change_surname)
async def handle_change_surname_message(message: types.Message,state=FSMContext):
    db.set_surname(message.from_user.id, message.text)
    await state.finish()
    await bot.send_message(message.from_user.id, 'Вы успешно изменили фамилию!')


# Отслеживает нажатие на кнопку "изменить имя"
@dp.callback_query_handler(text='change_name')
async def change_name_btn(callback: types.CallbackQuery):
    if not db.user_exists(callback.from_user.id):
        await bot.send_message(callback.from_user.id, 'Вы еще не зарегистрировались!')
        await callback.answer()
    else:
        await bot.send_message(callback.from_user.id, 'Введите имя на кириллице: ')
        await UserReg.change_name.set()
        await callback.answer()


# Ловит стейт на изменение имени
@dp.message_handler(state=UserReg.change_name)
async def handle_change_name_message(message: types.Message,state=FSMContext):
    db.set_name(message.from_user.id, message.text)
    await state.finish()
    await bot.send_message(message.from_user.id, 'Вы успешно изменили имя!')


# Отслеживает нажатие на кнопку "профиль"
@dp.callback_query_handler(text='show_profile')
async def show_profile(callback: types.CallbackQuery):
    if not db.user_exists(callback.from_user.id):
        await bot.send_message(callback.from_user.id, 'Вы еще не зарегистрировались!')
        await callback.answer()
    else:
        await bot.send_message(callback.from_user.id, db.show_profile(callback.from_user.id))
        await callback.answer()


# Ловит стейт для ввода номера телефона на этапе регистрации
@dp.message_handler(state=UserReg.phone_number)
async def handle_phone_number_message(message: types.Message,state=FSMContext):
    pattern = "^\\+?[1-9][0-9]{7,14}$"

    phone_number = message.text

    if re.match(pattern, phone_number) is not None:
        if not db.phone_exists(phone_number):
            db.set_phone_number(message.from_user.id, phone_number)
            await bot.send_message(message.from_user.id, 'Регистрация успешно завершена!')
            await bot.send_message(adm_chat_id,'ЗАРЕГИСТРИРОВАЛСЯ ПОЛЬЗОВАТЕЛЬ!\n' + db.show_profile(message.from_user.id))
            await state.finish()
        else:
            await UserReg.phone_number.set()
            await bot.send_message(message.from_user.id, 'Этот номер уже используется, посмотрите внимательнее на номер, который вы ввели!')
            await bot.send_message(message.from_user.id, 'Введите ваш номер телефона с кодом страны и без пробелов. Пример для заполнения: +77017299556')
    else:
        await bot.send_message(message.from_user.id, 'Номера телефона не соответствует формату')
        await UserReg.phone_number.set()
        await bot.send_message(message.from_user.id, 'Введите ваш номер телефона с кодом страны и без пробелов. Пример для заполнения: +77017299556')
       

# Ловит стейт для ввода отчества на этапе регистрации
@dp.message_handler(state=UserReg.patronymic)
async def handle_patronymic_message(message: types.Message,state=FSMContext):
    db.set_patronymic(message.from_user.id, message.text)
    await state.finish()
    await bot.send_message(message.from_user.id, 'Введите ваш номер телефона с кодом страны и без пробелов. Пример для заполнения: +77017299556')
    await UserReg.phone_number.set()

# Ловит стейт для ввода фамилии на этапе регистрации
@dp.message_handler(state=UserReg.surname)
async def handle_surname_message(message: types.Message,state=FSMContext):
    db.set_surname(message.from_user.id, message.text)
    await state.finish()
    await bot.send_message(message.from_user.id, 'Введите ваше отчество на кириллице: ')
    await UserReg.patronymic.set()


# Ловит стейт для ввода имени на этапе регистрации
@dp.message_handler(state=UserReg.name)
async def handle_name_message(message: types.Message,state=FSMContext):
    db.set_name(message.from_user.id, message.text)
    await state.finish()
    await bot.send_message(message.from_user.id, 'Введите вашу фамилию на кириллице: ')
    await UserReg.surname.set()


# Отслеживает нажатие на кнопку "Регистрация"
@dp.callback_query_handler(text='reg')
async def handle_reg_command(callback: types.CallbackQuery):
    if not db.user_exists(callback.from_user.id):
        db.add_user(callback.from_user.id, 'name', 'surname','phone_number', 'patronymic')
        await bot.send_message(callback.from_user.id, 'Введите ваше имя на кириллице: ')
        await UserReg.name.set()
    else:
        await bot.send_message(callback.from_user.id, 'Вы уже зарегистрированы')


# Для админов

# Добавляет группу в бд
@dp.message_handler(commands=['add_chat'])
async def handle_add_group_command(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member['status'] == 'creator' or member['status'] == 'administrator':
        if not db.chat_exists(message.chat.id):
            db.add_chat(message.chat.id, message.chat.title)
            await bot.send_message(message.chat.id, 'Группа успешно добавлена в базу')
        else:
            await bot.send_message(message.chat.id, 'Группа уже существует в базе')
    else:
        await bot.send_message(message.chat.id, 'У вас недостаточно прав')

async def send_chunked_messages(data, chat_id, check):
    if check == 0:
        chunk_size = 50  # Указываете размер чанка
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        
        for chunk in chunks:
            messages = []
            for row in chunk:
                txt = f'Имя: {row[0]}\nФамилия: {row[1]}\nОтчество: {row[2]}\nНомер телефона: {row[3]}\n'
                messages.append(txt)
            await bot.send_message(chat_id, '\n'.join(messages))
    else:
        chunk_size = 40  # Указываете размер чанка
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        
        for chunk in chunks:
            messages = []
            for row in chunk:
                # txt = f'Имя: {row[0]}\nФамилия: {row[1]}\nОтчество: {row[2]}\nНомер телефона: {row[3]}\n'
                txt = f'Имя: {row[0]}\nФамилия: {row[1]}\nОтчество: {row[3]}\nНомер телефона: {row[2]}\nГруппы: {row[4]}\n'
                messages.append(txt)
            await bot.send_message(chat_id, '\n'.join(messages))

@dp.message_handler(commands=['search'])
async def handle_search_by_name_command(message: types.Message):
    if message.chat.id == adm_chat_id:
        count_data = len(message.text.split())
        if count_data == 2:
            try:
                if '+' in message.text.split()[1]:
                    data = []

                    for result in db.search_info_by_phone(message.text.split()[1]):
                        data.append(result)
                        
                    if len(data) == 0:
                        await bot.send_message(adm_chat_id, 'Пользователь не найден')
                    else:   
                        await send_chunked_messages(data, adm_chat_id, 1)
                else:    
                    data = []

                    for result in db.get_info_by_name_or_surname(message.text.split()[1]):
                        data.append(result)
                        
                    if len(data) == 0:
                        await bot.send_message(adm_chat_id, 'Пользователь не найден')
                    else:   
                        await send_chunked_messages(data, adm_chat_id, 0)
                    
            except Exception as ex:
                await bot.send_message(adm_chat_id, f'Возникла ошибка:\n{ex}')
        elif count_data == 3:
            try:
                rez = message.text.split()
                name = rez[1]
                surname = rez[2]

                data = []

                for result in db.get_info_by_name_and_surname(name, surname):
                    data.append(result)

                if len(data) == 0:
                    await bot.send_message(adm_chat_id, 'Пользователь не найден')
                else:   
                    await send_chunked_messages(data, adm_chat_id, 1)
            except Exception as ex:
                await bot.send_message(adm_chat_id, f'Возникла ошибка:\n{ex}')
        elif count_data == 4:
            try:
                mess = message.text.split()
                surname = mess[1]
                name = mess[2]
                patronymic = mess[3]

                data = []
                for result in db.search_info_by_full_name(name, surname, patronymic):
                    data.append(result)
                if len(data) == 0:
                    await bot.send_message(adm_chat_id, 'Пользователь не найден')
                else:   
                    await send_chunked_messages(data, adm_chat_id, 1)
                    await asyncio.sleep(1)
                
            except Exception as ex:
                await bot.send_message(adm_chat_id, f'Возникла ошибка:\n{ex}')



# удаление юзера со всех групп
@dp.message_handler(commands=['kick'])
async def handle_search_by_phone_command(message: types.Message):
    if message.chat.id == adm_chat_id:
        try:
            mess = message.text.split()
            phone = mess[1]
            data = db.get_user_id_and_groups_by_phone(phone)

            user_id = data['user_id']
            groups = data['groups']

            if len(groups) == 0:
                await bot.send_message(adm_chat_id, f'Пользователь был удален из базы данных. В группах не состоял')
            else:    
                for group in groups:
                    if group[1] != adm_chat_id:
                        await bot.kick_chat_member(group[1], user_id)
                        await bot.send_message(message.chat.id, f'Пользователь был успешно удален из группы {group[0]}')
            
            db.delete_from_bd(user_id)

        except Exception as ex:
            await bot.send_message(message.chat.id, f'{ex}')


@dp.message_handler()
async def handle_add_chat_members_table(message: types.Message):
    if message.chat.type != 'private':
        try:
            await bot.get_chat_member(message.chat.id, message.from_user.id)
            db.add_chat_member(message.from_user.id, message.chat.id)
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)