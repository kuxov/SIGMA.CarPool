import asyncio
import datetime
import json
import pytz
import requests
from requests.auth import HTTPBasicAuth

url = ''
basic = HTTPBasicAuth('', '')


async def get_user_role(user_id):
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/user/getrolebyid?id=' + str(user_id), auth=basic, headers=headers)
    if r.status_code == 200:
        return r.json()['result']['id']
    else:
        return 0


async def get_metro_id(station):
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/metro/getbyname?name=' + station, auth=basic, headers=headers)
    if r.status_code == 200:
        return r.json()['result']['id']
    else:
        return 0


async def register_driver(user):
    headers = {'Content-Type': 'application/json'}

    payload = {
        "id": user[0],
        "firstName": user[1],
        "role": {
            "id": 1
        },
        "phone": user[2],
        "tgLink": user[3],
        "bonus": 0,
        "benefits": "",
        "capacity": user[4],
        "registrationDate": datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%dT%H:%M:%S'),
        "metros": []

    }
    r = requests.post(url + '/api/v1/user/add', auth=basic, headers=headers, data=json.dumps(payload))
    print(r.text)
    print(payload)


async def register_passenger(user):
    headers = {'Content-Type': 'application/json'}

    payload = {
        "id": user[0],
        "firstName": user[1],
        "role": {
            "id": 2
        },
        "phone": user[2],
        "tgLink": user[3],
        "bonus": 0,
        "benefits": user[4],
        "capacity": 0,
        "registrationDate": datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%dT%H:%M:%S'),
        "metros": []

    }

    r = requests.post(url + '/api/v1/user/add', auth=basic, headers=headers, data=json.dumps(payload))
    print(r.text)
    print(payload)


async def add_metro(usr, data):
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/user/' + str(usr) + '/addmetro?metroId=' + str(data), auth=basic, headers=headers)
    print(r.text)


async def delete_metro(usr, data):
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/user/' + str(usr) + '/deletemetro?metroId=' + str(data), auth=basic,
                     headers=headers)
    print(r.text)


async def change_field(i, field, value, db):
    headers = {'Content-Type': 'application/json'}

    payload = {
        str(field): str(value)
    }

    db.update_field(i, value, field)
    r = requests.put(url + '/api/v1/user/' + str(i), auth=basic, headers=headers, data=json.dumps(payload))
    print(r.text)
    print(payload)


async def change_role(i, value):
    headers = {'Content-Type': 'application/json'}

    payload = {
        "role":
            {
                "id": str(value)
            }
    }

    r = requests.put(url + '/api/v1/user/' + str(i), auth=basic, headers=headers, data=json.dumps(payload))
    print(r.text)
    print(payload)


async def change_metro(i, field, value):
    headers = {'Content-Type': 'application/json'}

    value = await get_metro_id(value)

    if field == 'stations':  # bug - need multiple stations
        payload = {
            "metro": {
                "id": value
            }
        }
    elif field == 'station':
        payload = {
            "metro": {
                "id": value
            }
        }

    r = requests.put(url + '/api/v1/user/' + str(i), auth=basic, headers=headers, data=json.dumps(payload))
    print(r.text)
    print(payload)


async def current_trips_d(user):
    x = {}
    user_array = []
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/trip/gettripsbyuserid?userId=' + user, auth=basic, headers=headers)
    if r.status_code != 200:
        return 'Пока что активных поездок нет!('
    input_dict = r.json()
    output_dict = [x for x in input_dict['result'] if x['status']['id'] == 1]
    for item in output_dict:
        user_array = []
        for item2 in item['passengers']:
            user_array.append(str(item2['firstName'] + ' ' + str(item2['metros'][0]['name'])))

        x.update({item['id']: {item['tripDate']: user_array}})
    print(x)
    return x


async def current_trips_p(user):
    x = {}
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/trip/gettripsbyuserid?userId=' + user, auth=basic, headers=headers)
    if r.status_code != 200:
        return -1
    input_dict = r.json()
    output_dict = [x for x in input_dict['result'] if x['status']['id'] == 1]
    for item in output_dict:
        x.update({item['id']: {item['tripDate']: item['driver']['firstName']}})
    print(x)
    return x


async def annul_trip(i, user):
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/trip/' + i + '/close?userId=' + user, auth=basic, headers=headers)
    print(r.text)
    print(r.status_code)


async def delete_passenger(i, user):
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/trip/' + i + '/deletepassenger?userId=' + user, auth=basic, headers=headers)


async def create_day(data):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "days": data[0],
        "seats": data[1],
        "user": {
            "id": data[2]
        },
        "destination": {
            "id": data[3]
        }
    }

    r = requests.post(url + '/api/v1/day/add', auth=basic, headers=headers, data=json.dumps(payload))
    print(r.status_code)
    print(payload)
    return r.json()['result']


async def create_trip(data, day_id, station_id):
    headers = {'Content-Type': 'application/json'}

    payload = {

        "driver": {
            "id": data[2]
        },
        "passengers": [],
        "status": {
            "id": 1
        },
        "destination": {
            "id": data[3]
        },
        "tripDate": data[0],
        "day": {
            "id": day_id
        },
        "metro": {
            "id": station_id
        }

    }

    r = requests.post(url + '/api/v1/trip/add', auth=basic, headers=headers, data=json.dumps(payload))
    print(r.status_code)
    print(r.text)
    print(payload)
    return r.json()['result']


async def find_trips(data):
    headers = {'Content-Type': 'application/json'}

    station = await get_metro_id(data[3])

    payload = {
        "dateTrip": data[0],
        "metro": station,
        "destination": data[2]
    }

    r = requests.post(url + '/api/v1/trip/findtrips', auth=basic, headers=headers, data=json.dumps(payload))
    print(r.text)

    x = {}

    input_dict = r.json()
    output_dict = [x for x in input_dict['result'] if x['status']['id'] == 1]
    for item in output_dict:
        x.update({item['id']: [{item['tripDate']: item['driver']['firstName']}, {"id": item['driver']['id']}]})
    print(x)
    return x


async def add_passenger(i, user):
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/trip/' + i + '/addpassenger?passengerId=' + user, auth=basic, headers=headers)
    print(r.text)
    print(r.content)


async def return_date(user, trip):
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url + '/api/v1/trip/gettripsbyuserid?userId=' + str(user), auth=basic, headers=headers)

    input_dict = r.json()
    output_dict = {}
    for item in input_dict['result']:
        if item['id'] == int(trip):
            output_dict.update({'dt': item})

    print(output_dict['dt']['tripDate'])
    return output_dict['dt']['tripDate']


if __name__ == '__main__':
    asyncio.run(return_date(739808500, 36))
