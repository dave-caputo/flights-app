from datetime import datetime
import re
import requests
import sys

import pytz

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from scraper.source.utils import format_to_data_table


def get_response(operation, page=0):

    utc_now = timezone.now()

    # To get the list of all timezones loop over pytz.all_timezones
    # More info at https://www.youtube.com/watch?v=eirjjyP2qcQ
    amsterdam_tz = pytz.timezone('Europe/Amsterdam')
    now = utc_now.astimezone(amsterdam_tz)
    local_time = datetime.strftime(now, '%H:%M')

    # More info at https://developer.schiphol.nl/apis/flight-api/flights
    url = 'https://api.schiphol.nl/public-flights/flights'
    querystring = {
        'app_id': '7e07d59a',
        'app_key': settings.SCHIPHOL_KEY,
        'flightdirection': operation[0].upper(),
        'includedelays': 'true',
        'page': page,
        'scheduletime': local_time
    }
    headers = {'resourceversion': 'v3'}

    try:
        response = requests.request("GET", url,
                                    headers=headers,
                                    params=querystring)
        return response
    except requests.exceptions.ConnectionError as error:
        print('Unable to get data from page {}'.format(page))


def update_flight_data(flights):
    destinations = cache.get('destinations')
    updated_flight_list = []
    for f in flights:

        # Consider only Passenger Line services
        if f['serviceType'] != "J":
            continue

        f['scheduledTimestamp'] = f.pop('scheduleTime')

        f['city'] = f['route']['destinations'][0]

        # Translate city code to city name.
        route = f.pop('route')
        city_code = route['destinations'][0]
        try:
            f['city'] = (
                d['city'] for d in destinations if d['iata'] == city_code
            ).__next__()
        except StopIteration:
            f['city'] = 'Not Available'

        f['flightNumber'] = f.pop('flightName')
        f['terminalId'] = f.pop('terminal', 'Not Available')

        status = f.pop('publicFlightState')
        f['flightOutputStatus'] = status['flightStates'][0]

        updated_flight_list.append(f)

    return updated_flight_list


def get_flight_page_count(operation):
    response = get_response(operation)
    link = response.headers['Link']
    page_count = re.findall(r'(?<=page\=)\d+', link)[0]
    return int(page_count)


@format_to_data_table
def get_schiphol_flights(operation):
    flight_list = []
    page_count = get_flight_page_count(operation)
    page = 0

    # try:
    #     destinations = cache.get('destinations')
    #     flight_list = cache.get('schiphol_{}'.format(operation))
    #     return flight_list

    # except KeyError:
    #    print("Unable to obtain cached Schiphol destinations or flights.")

    for page in range(0, page_count + 1):
        response = get_response(operation, page)

        # Check response type
        if response.status_code == 500:
            print('Http 500: API responded with an internal server error.')
            break

        elif response.status_code == 200:
            response_data = response.json()

            # For each flight align keys and values with template.
            flights = update_flight_data(response_data['flights'])

            flight_list += flights

    # Cache if the flight list is not empty:
    if flight_list:
        cache.set('schipol_{}'.format(operation), flight_list, None)

    return flight_list


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
