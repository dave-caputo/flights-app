import requests
import sys

from django.conf import settings

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
        f = response.json()
        flightList = f['flights']
        print(flightList)
        for f in flightList:
            f['scheduledTimestamp'] = f['scheduleTime']
            f['city'] = ", ".join(f['route']['destinations'])
            f['flightNumber'] = f['flightName']
            f['terminalId'] = f['terminal']
            f['flightOutputStatus'] = f['publicFlightState']['flightStates'][0]
        return flightList
