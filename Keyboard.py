from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardRemove

from Text import ALL_OK, BECAME_A_PASSENGER

DRIVER_OR_PASSENGER_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(KeyboardButton("Я водитель"),
                              KeyboardButton("Я пассажир"))

YES_NO_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(KeyboardButton("Да"), KeyboardButton("Нет")
                              )

DRIVER_ACTIONS_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(KeyboardButton("Мои поездки"),
                              KeyboardButton("Создать поездку"),
                              KeyboardButton("Редактировать профиль")
                              )

PASSENGER_ACTIONS_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(KeyboardButton("Мои поездки"),
                              KeyboardButton("Найти поездку"),
                              KeyboardButton("Редактировать профиль")
                              )

HIDE_KEYBOARD = ReplyKeyboardRemove()

LITTLE_EXPERIENCE_WARNING_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(KeyboardButton(ALL_OK)).row(
    KeyboardButton(BECAME_A_PASSENGER))

MY_RIDES_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(KeyboardButton("Вернуться в меню"))

EDIT_DRIVER_PROFILE_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(KeyboardButton("Имя")).row(
    KeyboardButton("Контактный номер")).row(
    KeyboardButton("Проезжаемые станции")).row(
    KeyboardButton("Свободные места в машине")).row(
    KeyboardButton("Стать пассажиром!")).row(
    KeyboardButton("Отмена")
)

EDIT_PASSENGER_PROFILE_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(KeyboardButton("Имя")).row(
    KeyboardButton("Контактный номер")).row(
    KeyboardButton("Возможная польза")).row(
    KeyboardButton("Станция метро")).row(
    KeyboardButton("Стать водителем!")).row(
    KeyboardButton("Отмена")
)

CHOOSE_RIDE_DIRECTION_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(
    KeyboardButton("В офис"), KeyboardButton("Из офиса")).row(
    KeyboardButton("Начать заново")
)

CHOOSE_RIDE_DATE_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(
    KeyboardButton("Сегодня"), KeyboardButton("Завтра"),
    KeyboardButton("Через 2 дня")
).row(KeyboardButton("Начать заново"))

ADD_RIDE_COMMENT_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(
    KeyboardButton("Пропустить")
).row(KeyboardButton("Начать заново"))

CONFIRM_RIDE_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True).row(
    KeyboardButton("Подтвердить")
).row(KeyboardButton("Отменить"))