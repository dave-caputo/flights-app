import re
import requests
import sys

from django.conf import settings
from django.core.cache import cache

from scraper.source.utils import format_to_data_table


@format_to_data_table
def get_schiphol_flights(operation):
    url = "https://api.schiphol.nl/public-flights/flights"
    querystring = {
        'app_id': '7e07d59a',
        'app_key': settings.SCHIPHOL_KEY,
        'flightdirection': operation[0].upper(),
        'includedelays': 'true'}
    headers = {
        'resourceversion': "v3"
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
    except requests.exceptions.ConnectionError as error:
        print(error)
        sys.exit()
    if response.status_code == 200:
        destinations = cache.get('destinations')
        print(response.headers)
        f = response.json()
        flightList = f['flights']
        for f in flightList:
            f['scheduledTimestamp'] = f['scheduleTime']

            city_code = f['route']['destinations'][0]
            f['city'] = (
                d['city'] for d in destinations if d['iata'] == city_code
            ).__next__()

            f['flightNumber'] = f['flightName']
            f['terminalId'] = f['terminal']
            f['flightOutputStatus'] = f['publicFlightState']['flightStates'][0]
        return flightList


def get_destinations():
    url = 'https://api.schiphol.nl/public-flights/destinations'
    querystring = {
        'app_id': '7e07d59a',
        'app_key': settings.SCHIPHOL_KEY,
        'sort': '+city'
    }
    headers = {
        'resourceversion': 'v1'
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
    except requests.exceptions.ConnectionError as error:
        print(error)
        sys.exit()
    if response.status_code == 200:
        link = response.headers['Link']
        print(link)
        pages = re.findall(r'(?<=page\=)\d+', link)
        d = response.json()
        destinations = d['destinations']
        for page in range(1, int(pages[0]) + 1):
            url = 'https://api.schiphol.nl/public-flights/destinations'
            querystring = {
                'app_id': '7e07d59a',
                'app_key': settings.SCHIPHOL_KEY,
                'sort': '+city',
                'page': page
            }

            headers = {
                'resourceversion': 'v1'
            }
            try:
                response = requests.request("GET", url, headers=headers, params=querystring)
            except requests.exceptions.ConnectionError as error:
                print(error)
                sys.exit()
            if response.status_code == 200:
                d = response.json()
                destinations += d['destinations']

        cache.set('destinations', destinations, None)
        return destinations

        # cache.set('destinations', destinations, None)
        #return destinations
