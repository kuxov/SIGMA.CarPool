import random
import string

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import *
from aiogram.types import message
from aiogram.utils import executor

import Text
from Keyboard import *
from Requests import *
from States import *
from User import *

TOKEN = ""
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
user = User()


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):

    user.id = msg.from_user.id
    print(user.id)
    sw = await get_user_role(user.id)
    user.tg_link = msg.from_user.username

    # user.id = random.randint(50000, 100001)
    # sw = await get_user_role(user.id)
    # user.tg_link = randomword(10)

    match sw:
        case 1:
            await msg.answer('Привет!👋 \nЧто вы хотите сделать?', reply_markup=DRIVER_ACTIONS_KEYBOARD)
            await UserStates.IDLE_D.set()
        case 2:
            await msg.answer('Привет!👋 \nЧто вы хотите сделать?', reply_markup=PASSENGER_ACTIONS_KEYBOARD)
            await UserStates.IDLE_P.set()
        case 0:
            await msg.answer(Text.REGISTRATION_STARTED_MESSAGE)
            await msg.answer(Text.ARE_YOU_EMPLOYED_QUESTION, reply_markup=YES_NO_KEYBOARD)
            await UserStates.REGISTER.set()


@dp.message_handler(state=UserStates.REGISTER)
async def start_registering(msg: types.Message):
    if msg.text == 'Нет':
        await msg.answer(Text.ARENT_EMPLOYED_MESSAGE, reply_markup=types.ReplyKeyboardRemove())
        await UserStates.BANNED.set()
    elif msg.text == 'Да':
        await msg.answer(Text.WHATS_YOUR_NAME_QUESTION, reply_markup=types.ReplyKeyboardRemove())
        await REGISTRATION.GET_NAME.set()


@dp.message_handler(state=REGISTRATION.GET_NAME)
async def r_set_name(msg: types.Message):
    # check string
    user.name = msg.text
    await msg.answer(Text.WHATS_YOUR_PHONE_NUMBER_QUESTION, reply_markup=types.ReplyKeyboardRemove())
    await REGISTRATION.GET_NUMBER.set()


@dp.message_handler(state=REGISTRATION.GET_NUMBER)
async def r_set_phone(msg: types.Message):
    # check string
    user.phone = msg.text
    await msg.answer('Кто вы?', reply_markup=DRIVER_OR_PASSENGER_KEYBOARD)
    await REGISTRATION.GET_ROLE.set()


@dp.message_handler(state=REGISTRATION.GET_ROLE)
async def r_chosen_role(msg: types.Message):
    if msg.text == 'Я водитель':
        await msg.answer(Text.DRIVER_EXPERIENCE_QUESTION, reply_markup=types.ReplyKeyboardRemove())
        await REGISTRATION.GET_EXP_D.set()
    elif msg.text == 'Я пассажир':
        await msg.answer(Text.WHERE_ARE_PASSENGER_LIVING_QUESTION, reply_markup=types.ReplyKeyboardRemove())
        await REGISTRATION.GET_STATION_P.set()


@dp.message_handler(state=REGISTRATION.GET_EXP_D, regexp=r'[0-9]+ (год|лет)')
async def r_driver_exp(msg: types.Message):
    if int(msg.text.split()[0]) < 1:
        await msg.answer(Text.LESS_THAN_ONE_YEAR_EXPERIENCE_WARNING,
                         reply_markup=LITTLE_EXPERIENCE_WARNING_KEYBOARD)
        await REGISTRATION.WARN_D.set()
    else:
        await msg.answer(Text.WHICH_STATIONS_WILL_BE_PASSED_QUESTION,
                         reply_markup=types.ReplyKeyboardRemove())
        await REGISTRATION.GET_STATIONS_D.set()


@dp.message_handler(lambda msg: msg.text == ALL_OK or BECAME_A_PASSENGER,
                    state=REGISTRATION.WARN_D)
async def r_warn_driver(msg: types.Message):
    if msg.text == ALL_OK:
        await msg.answer(Text.WHICH_STATIONS_WILL_BE_PASSED_QUESTION,
                         reply_markup=types.ReplyKeyboardRemove())
        await REGISTRATION.GET_STATIONS_D.set()
    elif msg.text == BECAME_A_PASSENGER:
        await msg.answer(Text.WHERE_ARE_PASSENGER_LIVING_QUESTION,
                         reply_markup=types.ReplyKeyboardRemove())
        await REGISTRATION.GET_STATION_P.set()


@dp.message_handler(state=REGISTRATION.GET_STATIONS_D)
async def get_stations(msg: types.Message):
    user.metro = msg.text.split(", ")
    await msg.answer(Text.HOW_MANY_FREE_SLOTS_QUESTION,
                     reply_markup=types.ReplyKeyboardRemove())
    await REGISTRATION.GET_CAPACITY_D.set()


@dp.message_handler(state=REGISTRATION.GET_STATION_P)
async def get_station(msg: types.Message):
    user.metro = msg.text
    await msg.answer(Text.HOW_WILL_BENEFIT_QUESTION,
                     reply_markup=types.ReplyKeyboardRemove())
    await REGISTRATION.GET_BENEFITS_P.set()


@dp.message_handler(state=REGISTRATION.GET_CAPACITY_D)
async def get_station(msg: types.Message):
    user.capacity = msg.text
    await register_driver(user)
    await msg.answer(Text.REGISTRARION_ENDED_MESSAGE,
                     reply_markup=DRIVER_ACTIONS_KEYBOARD)
    await UserStates.IDLE_D.set()


@dp.message_handler(state=REGISTRATION.GET_BENEFITS_P)
async def get_station(msg: types.Message):
    user.benefits = msg.text
    await register_passenger(user)
    await msg.answer(Text.REGISTRARION_ENDED_MESSAGE,
                     reply_markup=PASSENGER_ACTIONS_KEYBOARD)
    await UserStates.IDLE_P.set()


@dp.message_handler(state=UserStates.IDLE_D)
async def choose_action_d(msg: types.Message):
    print('IDLE_D')

    match msg.text:
        case "Мои поездки":
            await msg.answer('Ваши актуальные поездки:',
                             reply_markup=MY_RIDES_KEYBOARD)
            await UserStates.ACTUAL_TRIPS_D.set()
        case "Создать поездку":
            pass
        case "Редактировать профиль":
            await msg.answer('Что вы хотите поменять?',
                             reply_markup=EDIT_DRIVER_PROFILE_KEYBOARD)
            await UserStates.UPDATE_PROFILE_D.set()


@dp.message_handler(state=UserStates.IDLE_P)
async def choose_action_p(msg: types.Message):
    print('IDLE_P')

    match msg.text:
        case "Мои поездки":
            await msg.answer('Ваши актуальные поездки:',
                             reply_markup=MY_RIDES_KEYBOARD)
            await UserStates.ACTUAL_TRIPS_P.set()
        case "Найти поездку":
            pass
        case "Редактировать профиль":
            await msg.answer('Что вы хотите поменять?',
                             reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
            await UserStates.UPDATE_PROFILE_P.set()


########################################################################################################################
# Редактировать профиль


@dp.message_handler(state=UserStates.UPDATE_PROFILE_D)
async def driver_choose_update(msg: types.Message):
    print('UPDATE_PROFILE_D')

    match msg.text:
        case "Имя":
            await msg.answer(Text.WHATS_YOUR_NAME_QUESTION,
                             reply_markup=types.ReplyKeyboardRemove())
            await DRIVER.UPD_NAME.set()
        case "Контактный номер":
            await msg.answer(Text.WHATS_YOUR_PHONE_NUMBER_QUESTION,
                             reply_markup=types.ReplyKeyboardRemove())
            await DRIVER.UPD_NUMBER.set()
        case "Проезжаемые станции":
            await msg.answer(Text.WHICH_STATIONS_WILL_BE_PASSED_QUESTION,
                             reply_markup=types.ReplyKeyboardRemove())
            await DRIVER.UPD_STATIONS_D.set()
        case "Свободные места в машине":
            await msg.answer(Text.HOW_MANY_FREE_SLOTS_QUESTION,
                             reply_markup=types.ReplyKeyboardRemove())
            await DRIVER.UPD_CAPACITY.set()
        case "Стать пассажиром!":
            await change_role(msg.from_user.id, 2)
            await msg.answer('Успех! \nТеперь нужно восстановить часть данных.',
                             reply_markup=HIDE_KEYBOARD)
            await msg.answer(Text.HOW_WILL_BENEFIT_QUESTION,
                             reply_markup=HIDE_KEYBOARD)
            await PASSENGER.UPD_BENEFITS.set()
        case "Отмена":
            await msg.answer('Что вы хотите сделать?',
                             reply_markup=DRIVER_ACTIONS_KEYBOARD)
            await UserStates.IDLE_D.set()


@dp.message_handler(state=DRIVER.UPD_NAME)
async def d_change_name(msg: types.Message):
    await change_field(msg.from_user.id, 'firstName', msg.text)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_DRIVER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_D.set()


@dp.message_handler(state=DRIVER.UPD_NUMBER)
async def d_change_num(msg: types.Message):
    await change_field(msg.from_user.id, 'phone', msg.text)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_DRIVER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_D.set()


@dp.message_handler(state=DRIVER.UPD_STATIONS_D)
async def d_change_metro(msg: types.Message):
    await change_metro(msg.from_user.id, 'stations', msg.text)  # bug - need multiple stations
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_DRIVER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_D.set()


@dp.message_handler(state=DRIVER.UPD_CAPACITY)
async def d_change_capacity(msg: types.Message):
    await change_field(msg.from_user.id, 'capacity', msg.text)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_DRIVER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_D.set()


@dp.message_handler(state=UserStates.UPDATE_PROFILE_P)
async def passenger_choose_update(msg: types.Message):
    print('UPDATE_PROFILE_P')
    match msg.text:
        case "Имя":
            await msg.answer(Text.WHATS_YOUR_NAME_QUESTION,
                             reply_markup=types.ReplyKeyboardRemove())
            await PASSENGER.UPD_NAME.set()
        case "Контактный номер":
            await msg.answer(Text.WHATS_YOUR_PHONE_NUMBER_QUESTION,
                             reply_markup=types.ReplyKeyboardRemove())
            await PASSENGER.UPD_NUMBER.set()
        case "Станция метро":
            await msg.answer(Text.WHICH_STATIONS_WILL_BE_PASSED_QUESTION,
                             reply_markup=types.ReplyKeyboardRemove())
            await PASSENGER.UPD_STATION_P.set()
        case "Возможная польза":
            await msg.answer(Text.HOW_WILL_BENEFIT_QUESTION,
                             reply_markup=types.ReplyKeyboardRemove())
            await PASSENGER.UPD_BENEFITS.set()
        case "Стать водителем!":
            await change_role(msg.from_user.id, 1)
            await msg.answer('Успех! \nТеперь нужно восстановить часть данных.',
                             reply_markup=HIDE_KEYBOARD)
            await msg.answer(Text.HOW_MANY_FREE_SLOTS_QUESTION,
                             reply_markup=HIDE_KEYBOARD)
            await DRIVER.UPD_CAPACITY.set()
        case "Отмена":
            await msg.answer('Что вы хотите сделать?',
                             reply_markup=PASSENGER_ACTIONS_KEYBOARD)
            await UserStates.IDLE_P.set()


@dp.message_handler(state=PASSENGER.UPD_NAME)
async def p_change_name(msg: types.Message):
    await change_field(msg.from_user.id, 'firstName', msg.text)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_P.set()


@dp.message_handler(state=PASSENGER.UPD_NUMBER)
async def p_change_num(msg: types.Message):
    await change_field(msg.from_user.id, 'phone', msg.text)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_P.set()


@dp.message_handler(state=PASSENGER.UPD_STATION_P)
async def p_change_metro(msg: types.Message):
    await change_metro(msg.from_user.id, 'station', msg.text)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_P.set()


@dp.message_handler(state=PASSENGER.UPD_BENEFITS)
async def p_change_benefits(msg: types.Message):
    await change_field(msg.from_user.id, 'benefits', msg.text)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_P.set()


########################################################################################################################
# Заглушки

@dp.message_handler(state=UserStates.ACTUAL_TRIPS_D)
async def stub1(msg: types.Message):
    print('ACTUAL_TRIPS_D')

    if msg.text == 'Вернуться в меню':
        await msg.answer('Что вы хотите сделать?',
                         reply_markup=DRIVER_ACTIONS_KEYBOARD)
        await UserStates.IDLE_D.set()


@dp.message_handler(state=UserStates.ACTUAL_TRIPS_P)
async def stub2(msg: types.Message):
    print('ACTUAL_TRIPS_P')

    if msg.text == 'Вернуться в меню':
        await msg.answer('Что вы хотите сделать?',
                         reply_markup=PASSENGER_ACTIONS_KEYBOARD)
        await UserStates.IDLE_P.set()


########################################################################################################################


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
