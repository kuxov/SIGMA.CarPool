from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    REGISTER = State()
    IDLE_D = State()
    IDLE_P = State()
    ACTUAL_TRIPS_D = State()
    ACTUAL_TRIPS_P = State()
    CREATE_TRIP_D = State()
    FIND_TRIP_P = State()
    UPDATE_PROFILE_D = State()
    UPDATE_PROFILE_P = State()
    BANNED = State()


class REGISTRATION(StatesGroup):
    GET_NAME = State()
    GET_NUMBER = State()
    GET_ROLE = State()
    GET_EXP_D = State()
    GET_STATIONS_D = State()
    GET_STATION_P = State()
    GET_CAPACITY_D = State()
    GET_BENEFITS_P = State()
    WARN_D = State()


class DRIVER(StatesGroup):
    UPD_NAME = State()
    UPD_NUMBER = State()
    UPD_ROLE = State()
    UPD_STATIONS_D = State()
    UPD_CAPACITY = State()


class PASSENGER(StatesGroup):
    UPD_NAME = State()
    UPD_NUMBER = State()
    UPD_ROLE = State()
    UPD_STATION_P = State()
    UPD_BENEFITS = State()
