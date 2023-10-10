from aiogram.dispatcher.filters.state import State, StatesGroup


class UserReg(StatesGroup):
    name = State()
    surname = State()
    phone_number = State()
    patronymic = State()
    change_name = State()
    change_surname = State()
    change_phone = State()
    change_patronymic = State()