import random
import re
import string
from datetime import timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import loader
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import *
from aiogram.types import message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import logging
import Text
from Keyboard import *
from Requests import *
from States import *
from User import *

TOKEN = ''
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
db = DB()
scheduler = AsyncIOScheduler()


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


async def send_leaders():
    lst = await get_leader()

    txt = 'Поздравляю!\nВы набрали наибольшее количество баллов в этом месяце!!✨'

    for key in lst.keys():
        await bot.send_message(chat_id=key, text=txt, reply_markup=HIDE_KEYBOARD)


async def send_msg_d(i):
    txt = 'Напоминаю, что у вас начинается поездка через полчаса!'
    await bot.send_message(chat_id=i, text=txt, reply_markup=HIDE_KEYBOARD)


async def send_msg_p(data, i):
    txt = 'Напоминаю, что ' + data + ' начинает поездку через полчаса!'
    await bot.send_message(chat_id=i, text=txt, reply_markup=HIDE_KEYBOARD)


async def send_approval(data, i, key):
    txt = 'Ваша поездка с ' + data + ' состоялась ?'
    buttons = [[
        types.InlineKeyboardButton(text="Да 😎", callback_data="yes" + str(key)),
        types.InlineKeyboardButton(text="Нет 😡", callback_data="no" + str(key))
    ]]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_message(chat_id=i, text=txt, reply_markup=keyboard)


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    user_id = msg.from_user.id
    # user_id = random.randint(50000, 100001)
    tg_link = msg.from_user.username
    chat_id = msg.chat.id

    sw = await get_user_role(user_id)

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
            db.user_init(user_id, chat_id, tg_link)
            await msg.answer(Text.ARE_YOU_EMPLOYED_QUESTION, reply_markup=YES_NO_KEYBOARD)
            await UserStates.REGISTER.set()


@dp.message_handler(state=UserStates.REGISTER)
async def start_registering(msg: types.Message):
    if msg.text == 'Нет':
        await msg.answer(Text.ARENT_EMPLOYED_MESSAGE, reply_markup=types.ReplyKeyboardRemove())
        db.delete_user(msg.from_user.id)
        await UserStates.BANNED.set()
    elif msg.text == 'Да':
        await msg.answer(Text.WHATS_YOUR_NAME_QUESTION, reply_markup=types.ReplyKeyboardRemove())
        await REGISTRATION.GET_NAME.set()


@dp.message_handler(state=REGISTRATION.GET_NAME)
async def r_set_name(msg: types.Message):
    # check string
    db.set_name(msg.text, msg.from_user.id)
    await msg.answer(Text.WHATS_YOUR_PHONE_NUMBER_QUESTION, reply_markup=types.ReplyKeyboardRemove())
    await REGISTRATION.GET_NUMBER.set()


@dp.message_handler(state=REGISTRATION.GET_NUMBER)
async def r_set_phone(msg: types.Message):
    db.set_phone(msg.text, msg.from_user.id)
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
    db.set_metro(msg.text, msg.from_user.id)
    await msg.answer(Text.HOW_MANY_FREE_SLOTS_QUESTION,
                     reply_markup=types.ReplyKeyboardRemove())
    await REGISTRATION.GET_CAPACITY_D.set()


@dp.message_handler(state=REGISTRATION.GET_STATION_P)
async def get_station(msg: types.Message):
    db.set_metro(msg.text, msg.from_user.id)
    await msg.answer(Text.HOW_WILL_BENEFIT_QUESTION,
                     reply_markup=types.ReplyKeyboardRemove())
    await REGISTRATION.GET_BENEFITS_P.set()


@dp.message_handler(state=REGISTRATION.GET_CAPACITY_D)
async def get_capacity(msg: types.Message):
    db.set_capacity(msg.text, msg.from_user.id)

    await register_driver(db.get_driver_r(msg.from_user.id))
    stations = (db.get_driver_r(msg.from_user.id)[5]).split(', ')
    for item in stations:
        metro = await get_metro_id(item)
        await add_metro(msg.from_user.id, metro)

    await msg.answer(Text.REGISTRARION_ENDED_MESSAGE,
                     reply_markup=DRIVER_ACTIONS_KEYBOARD)
    await UserStates.IDLE_D.set()


@dp.message_handler(state=REGISTRATION.GET_BENEFITS_P)
async def get_benefits(msg: types.Message):
    db.set_benefits(msg.text, msg.from_user.id)

    await register_passenger(db.get_passenger_r(msg.from_user.id))
    station = await get_metro_id(db.get_passenger_r(msg.from_user.id)[5])
    await add_metro(msg.from_user.id, station)
    await msg.answer(Text.REGISTRARION_ENDED_MESSAGE,
                     reply_markup=PASSENGER_ACTIONS_KEYBOARD)
    await UserStates.IDLE_P.set()


@dp.callback_query_handler(state=UserStates.ACTUAL_TRIPS_D)
async def process_callback_decline_d(callback_query: types.CallbackQuery):
    code = ''.join(filter(lambda i: i.isdigit(), callback_query.data))

    await annul_trip(str(code), str(callback_query.from_user.id))
    await callback_query.message.answer(text='Поездка удалена!')


@dp.callback_query_handler(state=UserStates.ACTUAL_TRIPS_P)
async def process_callback_decline_p(callback_query: types.CallbackQuery):
    code = ''.join(filter(lambda i: i.isdigit(), callback_query.data))

    await delete_passenger(str(code), str(callback_query.from_user.id))
    await callback_query.message.answer(text='Вы исключены из поездки!')


@dp.message_handler(state=UserStates.IDLE_D)
async def choose_action_d(msg: types.Message):
    print('IDLE_D')

    match msg.text:
        case "Мои поездки":

            await msg.answer('Ваши актуальные поездки:',
                             reply_markup=MY_RIDES_KEYBOARD)
            data = await current_trips_d(str(msg.from_user.id))
            for key in data:
                print(key)
                await msg.answer(data[key], reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton('Отменить', callback_data='decline' + str(key))))

            await UserStates.ACTUAL_TRIPS_D.set()

        case "Создать поездку":
            await msg.answer('Формирование поездки', reply_markup=HIDE_KEYBOARD)

            buttons = [
                [
                    types.InlineKeyboardButton(text="В офис💼", callback_data="destination_1"),
                    types.InlineKeyboardButton(text="Из офиса🏠", callback_data="destination_2")
                ],
                # [types.InlineKeyboardButton(text="Начать сначала", callback_data="destination_3")]
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

            await msg.answer('Выберите направление поездки', reply_markup=keyboard)
            await CREATE_TRIP.SET_DESTINATION.set()

        case "Редактировать профиль":
            await msg.answer('Что вы хотите поменять?',
                             reply_markup=EDIT_DRIVER_PROFILE_KEYBOARD)
            await UserStates.UPDATE_PROFILE_D.set()


########################################################################################################################
# Создание поездки
@dp.callback_query_handler(state=CREATE_TRIP.SET_DESTINATION)
async def process_callback_destination_d(callback_query: types.CallbackQuery):
    code = ''.join(filter(lambda i: i.isdigit(), callback_query.data))

    match code:
        case '1':
            db.set_trip_field(callback_query.from_user.id, 1, 'destination')
        case '2':
            db.set_trip_field(callback_query.from_user.id, 2, 'destination')
    # case '3':
    #    await UserStates.CREATE_TRIP_D.set()

    await callback_query.message.answer('Успех!', reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True).row(KeyboardButton("Продолжить")))
    await CREATE_TRIP.SET_DATE.set()


@dp.callback_query_handler(state=CREATE_TRIP.SET_DATE)
async def process_callback_date_d(callback_query: types.CallbackQuery):
    code = ''.join(filter(lambda i: i.isdigit(), callback_query.data))

    match code:
        case '1':
            db.set_trip_field(callback_query.from_user.id, (
                    datetime.now(pytz.timezone('Europe/Moscow')) +
                    timedelta(days=0)).strftime('%Y-%m-%d'), 'trip_date')
        case '2':
            db.set_trip_field(callback_query.from_user.id, (
                    datetime.now(pytz.timezone('Europe/Moscow')) +
                    timedelta(days=1)).strftime('%Y-%m-%d'), 'trip_date')
        case '3':
            db.set_trip_field(callback_query.from_user.id, (
                    datetime.now(pytz.timezone('Europe/Moscow')) +
                    timedelta(days=2)).strftime('%Y-%m-%d'), 'trip_date')

    #  case '4':
    #     await UserStates.CREATE_TRIP_D.set()

    await callback_query.message.answer(text='Успех!')
    await callback_query.message.answer('Выберите время поездки \nНапример 09:30')
    await CREATE_TRIP.SET_TIME.set()


@dp.message_handler(state=CREATE_TRIP.SET_DATE)
async def create_trip_set_date(msg: types.Message):
    await msg.answer('Определяем дату поездки', reply_markup=HIDE_KEYBOARD)

    buttons = [
        [
            types.InlineKeyboardButton(text="Завтра", callback_data="date_2"),
            types.InlineKeyboardButton(text="Через два дня", callback_data="date_3")
        ],
        # [types.InlineKeyboardButton(text="Начать сначала", callback_data="date_4")]
    ]

    # if datetime.datetime.utcnow().hour < 17:
    buttons[0].insert(0, types.InlineKeyboardButton(text="Сегодня", callback_data="date_1"))

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await msg.answer('Выберите число поездки', reply_markup=keyboard)


@dp.callback_query_handler(state=CREATE_TRIP.CHECK)
async def process_callback_create_d(callback_query: types.CallbackQuery):
    code = ''.join(filter(lambda i: i.isdigit(), callback_query.data))

    match code:
        case '1':
            await callback_query.message.answer(text='Поездка успешно опубликована!')
            data = db.get_create_trip_info(callback_query.from_user.id)
            stations = (db.get_driver_r(callback_query.from_user.id)[5]).split(', ')
            day_id = await create_day(data)
            for item in stations:
                metro = await get_metro_id(item)
                await create_trip(data, day_id, metro)
        case '2':
            pass

    await callback_query.message.answer('Что вы хотите сделать?', reply_markup=DRIVER_ACTIONS_KEYBOARD)
    await UserStates.IDLE_D.set()


@dp.message_handler(state=CREATE_TRIP.SET_TIME)
async def create_trip_set_time(msg: types.Message):
    date_time = db.get_date(msg.from_user.id)

    db.set_trip_field(msg.from_user.id, date_time[0] + 'T' + msg.text + ':00', 'trip_date'
                      )

    buttons = [[
        types.InlineKeyboardButton(text="Подтвердить", callback_data="check_1"),
        types.InlineKeyboardButton(text="Отменить", callback_data="check_2")
    ]]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    data = db.get_create_trip_info(msg.from_user.id)

    lst = list(data)
    match lst[3]:
        case 1:
            lst[3] = "в Офис"
        case 2:
            lst[3] = "из Офиса"

    text = 'Все ли верно?'
    await msg.answer(text, reply_markup=HIDE_KEYBOARD)

    text = 'Маршрут: метро ' + lst[4] + ' ' + lst[3] + '\n' \
                                                       'Дата: ' + lst[0] + '\n'

    await msg.answer(text, reply_markup=keyboard)

    await CREATE_TRIP.CHECK.set()


########################################################################################################################


@dp.message_handler(state=UserStates.IDLE_P)
async def choose_action_p(msg: types.Message):
    print('IDLE_P')

    match msg.text:
        case "Мои поездки":
            await msg.answer('Ваши актуальные поездки:',
                             reply_markup=MY_RIDES_KEYBOARD)

            data = await current_trips_p(str(msg.from_user.id))
            for key in data:
                print(key)
                await msg.answer(data[key], reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton('Отменить', callback_data='decline' + str(key))))

            await UserStates.ACTUAL_TRIPS_P.set()
        case "Найти поездку":
            await msg.answer('Определим данные для поиска', reply_markup=HIDE_KEYBOARD)

            buttons = [
                [
                    types.InlineKeyboardButton(text="В офис💼", callback_data="destination_1"),
                    types.InlineKeyboardButton(text="Из офиса🏠", callback_data="destination_2")
                ],
                # [types.InlineKeyboardButton(text="Начать сначала", callback_data="destination_3")]
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

            await msg.answer('Выберите направление поездки', reply_markup=keyboard)
            await FIND_TRIP.SET_DESTINATION.set()
        case "Редактировать профиль":
            await msg.answer('Что вы хотите поменять?',
                             reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
            await UserStates.UPDATE_PROFILE_P.set()


########################################################################################################################
# Поиск поездки


@dp.callback_query_handler(state=FIND_TRIP.SET_DESTINATION)
async def process_callback_destination_p(callback_query: types.CallbackQuery):
    code = ''.join(filter(lambda i: i.isdigit(), callback_query.data))

    match code:
        case '1':
            db.set_trip_field(callback_query.from_user.id, 1, 'destination')
        case '2':
            db.set_trip_field(callback_query.from_user.id, 2, 'destination')
    #  case '3':
    #     await UserStates.FIND_TRIP_P.set()

    await callback_query.message.answer('Успех!', reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True).row(KeyboardButton("Продолжить")))
    await FIND_TRIP.SET_DATE.set()


@dp.callback_query_handler(state=FIND_TRIP.SET_DATE)
async def process_callback_date_p(callback_query: types.CallbackQuery):
    code = ''.join(filter(lambda i: i.isdigit(), callback_query.data))

    match code:
        case '1':
            db.set_trip_field(callback_query.from_user.id, (
                    datetime.now(pytz.timezone('Europe/Moscow')) +
                    timedelta(days=0)).strftime('%Y-%m-%dT00:00:00'), 'trip_date')
        case '2':
            db.set_trip_field(callback_query.from_user.id, (
                    datetime.now(pytz.timezone('Europe/Moscow')) +
                    timedelta(days=1)).strftime('%Y-%m-%dT00:00:00'), 'trip_date')
        case '3':
            db.set_trip_field(callback_query.from_user.id, (
                    datetime.now(pytz.timezone('Europe/Moscow')) +
                    timedelta(days=2)).strftime('%Y-%m-%dT00:00:00'), 'trip_date')
    #  case '4':
    #     await UserStates.FIND_TRIP_P.set()

    await callback_query.message.answer('Успех!', reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True).row(KeyboardButton("Продолжить")))

    await FIND_TRIP.FINALIZE.set()


@dp.message_handler(state=FIND_TRIP.SET_DATE)
async def create_trip_set_date(msg: types.Message):
    await msg.answer('Определяем дату поездки', reply_markup=HIDE_KEYBOARD)

    buttons = [
        [
            types.InlineKeyboardButton(text="Завтра", callback_data="date_2"),
            types.InlineKeyboardButton(text="Через два дня", callback_data="date_3")
        ],
        # [types.InlineKeyboardButton(text="Начать сначала", callback_data="date_4")]
    ]

    # if datetime.now(pytz.timezone('Europe/Moscow')).hour < 17:
    buttons[0].insert(0, types.InlineKeyboardButton(text="Сегодня", callback_data="date_1"))

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await msg.answer('Выберите число поездки', reply_markup=keyboard)


@dp.message_handler(state=FIND_TRIP.FINALIZE)
async def find_trip_finalize(msg: types.Message):
    buttons = [[
        types.InlineKeyboardButton(text="Начать поиск", callback_data="check_1"),
        types.InlineKeyboardButton(text="Отменить", callback_data="check_2")
    ]]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    data = db.get_find_trip_info(msg.from_user.id)

    lst = list(data)
    match lst[2]:
        case 1:
            lst[2] = "в Офис"
        case 2:
            lst[2] = "из Офиса"

    text = 'Все ли верно?'
    await msg.answer(text, reply_markup=HIDE_KEYBOARD)

    text = 'Маршрут: метро ' + str(lst[3]) + ' ' + str(lst[2]) + '\nДата: ' + str(lst[0][:-9]) + '\n'

    await msg.answer(text, reply_markup=keyboard)

    await FIND_TRIP.CHECK.set()


@dp.callback_query_handler(state=FIND_TRIP.CHECK)
async def process_callback_find_check(callback_query: types.CallbackQuery):
    code = ''.join(filter(lambda i: i.isdigit(), callback_query.data))

    match code:
        case '1':
            await callback_query.message.answer(text='Результаты поиска:')
            data = await find_trips(db.get_find_trip_info(callback_query.from_user.id))
            for key in data:
                print(key)
                print(str(data[key][1]['id']))
                await callback_query.message.answer(data[key][0], reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton('Подать заявку',
                                         callback_data='send' + str(data[key][1]['id']) + "$" + str(key))))

        case '2':
            pass
    await callback_query.message.answer('Что вы хотите сделать?', reply_markup=PASSENGER_ACTIONS_KEYBOARD)
    await UserStates.IDLE_P.set()


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
            await msg.answer('Успех! \nТеперь нужно восстановить часть данных.\n\nНе забудьте обновить станцию, '
                             'откуда вас забрать!!!',
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
    await change_field(msg.from_user.id, 'firstName', msg.text, db)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_DRIVER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_D.set()


@dp.message_handler(state=DRIVER.UPD_NUMBER)
async def d_change_num(msg: types.Message):
    await change_field(msg.from_user.id, 'phone', msg.text, db)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_DRIVER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_D.set()


@dp.message_handler(state=DRIVER.UPD_STATIONS_D)
async def d_change_metro(msg: types.Message):
    stations_to_delete = db.get_driver_r(msg.from_user.id)[5].split(', ')
    for item in stations_to_delete:
        metro = await get_metro_id(item)
        await delete_metro(msg.from_user.id, metro)

    db.update_field(msg.from_user.id, msg.text, 'metro')
    stations_to_update = msg.text.split(', ')
    for item in stations_to_update:
        metro = await get_metro_id(item)
        await add_metro(msg.from_user.id, metro)

    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_DRIVER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_D.set()


@dp.message_handler(state=DRIVER.UPD_CAPACITY)
async def d_change_capacity(msg: types.Message):
    await change_field(msg.from_user.id, 'capacity', msg.text, db)
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
            await msg.answer('Успех! \nТеперь нужно восстановить часть данных.\n\nНе забудьте обновить проезжаемые '
                             'станции метро!!!',
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
    await change_field(msg.from_user.id, 'firstName', msg.text, db)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_P.set()


@dp.message_handler(state=PASSENGER.UPD_NUMBER)
async def p_change_num(msg: types.Message):
    await change_field(msg.from_user.id, 'phone', msg.text, db)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_P.set()


@dp.message_handler(state=PASSENGER.UPD_STATION_P)
async def p_change_metro(msg: types.Message):
    stations_to_delete = db.get_driver_r(msg.from_user.id)[5].split(', ')
    for item in stations_to_delete:
        metro = await get_metro_id(item)
        await delete_metro(msg.from_user.id, metro)

    db.update_field(msg.from_user.id, msg.text, 'metro')
    stations_to_update = msg.text.split(', ')
    for item in stations_to_update:
        metro = await get_metro_id(item)
        await add_metro(msg.from_user.id, metro)

    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_P.set()


@dp.message_handler(state=PASSENGER.UPD_BENEFITS)
async def p_change_benefits(msg: types.Message):
    await change_field(msg.from_user.id, 'benefits', msg.text, db)
    await msg.answer('Успех! Что-то еще?',
                     reply_markup=EDIT_PASSENGER_PROFILE_KEYBOARD)
    await UserStates.UPDATE_PROFILE_P.set()


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
# Обработка и отсылка заявок

@dp.callback_query_handler(state='*')
async def process_request(callback_query: types.CallbackQuery):
    dollar = callback_query.data.split('$')
    code = ''.join(filter(lambda i: i.isdigit(), dollar[0]))

    if callback_query.data.startswith('send'):

        data = db.get_passenger_r(callback_query.from_user.id)

        text = "Вам поступила заявка от " + data[1] + "!\nНомер: " + data[2] + "\nТелеграм: @" + data[
            3] + "\nО себе: " + data[4] + "\nСтанция метро: " + data[5]

        buttons = [[
            types.InlineKeyboardButton(text="Принять",
                                       callback_data="post" + str(callback_query.from_user.id) + "$" + str(dollar[1])),
        ]]

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await bot.send_message(chat_id=code, text=text, reply_markup=keyboard)

    elif callback_query.data.startswith('post'):
        await add_passenger(dollar[1], code)

        data = db.get_driver_r(callback_query.from_user.id)

        text = data[1] + " принял(а) вашу заявку!" "!\nНомер: " + data[2] + "\nТелеграм: @" + data[3]

        await bot.send_message(chat_id=code, text=text)

        rd = datetime.strptime(await return_date(code, dollar[1]), '%Y-%m-%dT%H:%M:%S') + timedelta(
            seconds=4)  # + 2h
        rd1 = datetime.strptime(await return_date(code, dollar[1]), '%Y-%m-%dT%H:%M:%S') + timedelta(
            seconds=2)  # - 30m

        scheduler.add_job(send_approval, "date", run_date=rd, args=(data[1], code, dollar[1],))
        scheduler.add_job(send_msg_p, "date", run_date=rd1, args=(data[1], code,))
        scheduler.add_job(send_msg_d, "date", run_date=rd1, args=(callback_query.from_user.id,))
    elif callback_query.data.startswith('yes'):
        await annul_trip(code, str(callback_query.from_user.id))
    elif callback_query.data.startswith('no'):
        pass


########################################################################################################################

if __name__ == '__main__':
    scheduler.start()
    #scheduler.add_job(send_leaders, "cron", minute=1)
    #scheduler.add_job(db.get_total_num, "cron", minute=1)
    executor.start_polling(dp, skip_updates=True)

