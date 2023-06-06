import asyncio
import datetime
import json

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
    station = await get_metro_id(user.metro[0])
    payload = {
        "id": user.id,
        "firstName": user.name,
        "role": {
            "id": 1
        },
        "phone": user.phone,
        "tgLink": user.tg_link,
        "benefits": "",
        "capacity": user.capacity,
        "registrationDate": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
        "metro": {
            "id": station
        }
    }
    r = requests.post(url + '/api/v1/user/add', auth=basic, headers=headers, data=json.dumps(payload))
    print(r.text)
    print(payload)


async def register_passenger(user):
    headers = {'Content-Type': 'application/json'}
    station = await get_metro_id(user.metro)
    payload = {
        "id": user.id,
        "firstName": user.name,
        "role": {
            "id": 2
        },
        "phone": user.phone,
        "tgLink": user.tg_link,
        "benefits": user.benefits,
        "capacity": 0,
        "registrationDate": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
        "metro": {
            "id": station
        }
    }
    r = requests.post(url + '/api/v1/user/add', auth=basic, headers=headers, data=json.dumps(payload))
    print(r.text)
    print(payload)


async def change_field(i, field, value):
    headers = {'Content-Type': 'application/json'}

    payload = {
        str(field): str(value)
    }

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

