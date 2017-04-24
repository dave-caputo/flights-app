from datetime import datetime, timedelta
from operator import itemgetter
import re
import requests
import sys

import pytz

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from scraper.source.utils import format_to_data_table, merge_codeshare_flights


def get_local_datetime(max_interval=None, min_interval=None):

    # To get the list of all timezones loop over pytz.all_timezones
    # More info at https://www.youtube.com/watch?v=eirjjyP2qcQ
    utc_now = timezone.now()
    amsterdam_tz = pytz.timezone('Europe/Amsterdam')
    now = utc_now.astimezone(amsterdam_tz)

    local_datetime = {
        'now': now,
        'time_limits': False,
        'tz': amsterdam_tz
    }

    if max_interval and min_interval:
        str_time = lambda x: datetime.strftime(x, '%H:%M')
        local_datetime['time_limits'] = True

        max_time = now + timedelta(minutes=max_interval)
        local_datetime['max_time'] = max_time
        local_datetime['str_max_time'] = str_time(max_time)

        min_time = now - timedelta(minutes=min_interval)
        local_datetime['min_time'] = min_time
        local_datetime['str_min_time'] = str_time(min_time)

    return local_datetime


def get_response(operation, local_datetime, page=0):

    # More info at https://developer.schiphol.nl/apis/flight-api/flights
    url = 'https://api.schiphol.nl/public-flights/flights'
    querystring = {
        'app_id': '7e07d59a',
        'app_key': settings.SCHIPHOL_KEY,
        'flightdirection': operation[0].upper(),
        'includedelays': 'true',
        'page': page,
        'scheduletime': local_datetime.get('str_min_time', None),
        'sort': '+scheduleTime'  # No more filters available: API bug!
    }
    headers = {'resourceversion': 'v3'}
    try:
        response = requests.request("GET", url,
                                    headers=headers,
                                    params=querystring)
        return response
    except requests.exceptions.ConnectionError as error:
        print('Unable to get data from page {}'.format(page))


def update_flight_data(flights, local_datetime):

    destinations = cache.get('destinations')
    updated_flight_list = []

    for f in flights:

        str_scheduled_time = f['scheduleTime']
        t = datetime.strptime(str_scheduled_time, '%H:%M:%S')
        d = datetime.combine(local_datetime['now'].date(), t.time())
        scheduled_datetime = local_datetime['tz'].localize(d)

        if local_datetime['time_limits']:
            # Ignore if scheduled time is too early
            if scheduled_datetime < local_datetime['min_time']:
                continue

            # Stop the loop if max_time_limit is exceeded.
            if scheduled_datetime > local_datetime['max_time']:
                updated_flight_list.append("Max_time_exceeded")
                break

        # Consider only Passenger Line services
        if f['serviceType'] != "J":
            continue

        # Key aligned with template and 'seconds' info sliced off.
        f['scheduledTimestamp'] = f.pop('scheduleTime')[:-3]

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

        # Prepare data for translating status
        if f['actualOffBlockTime']:
            aobt = f['actualOffBlockTime'][11:-13]
        else:
            aobt = f['scheduledTimestamp']

        if f['publicEstimatedOffBlockTime']:
            peobt = f['publicEstimatedOffBlockTime'][11:-13]
        else:
            peobt = f['scheduledTimestamp']

        if f['actualLandingTime']:
            alt = f['actualLandingTime'][11:-13]
        else:
            alt = f['scheduledTimestamp']

        if f['estimatedLandingTime']:
            elt = f['estimatedLandingTime'][11:-13]
        else:
            elt = f['scheduledTimestamp']

        # Translate status.
        status = f.pop('publicFlightState')
        status = status['flightStates'][0]
        status_list = {
            # Arrivals
            'AIR': 'Expected {}'.format(elt),
            'ARR': 'Arrived {}'.format(alt),
            'EXP': 'Expected {}'.format(elt),
            'FIB': 'Expected {}'.format(elt),
            'FIR': 'Expected {}'.format(elt),
            'LND': 'Landed {}'.format(alt),

            # Departures
            'BRD': 'Boarding - Departing {}'.format(peobt),
            'DEL': 'Delayed {}'.format(peobt),
            'DEP': 'Departed {}'.format(aobt),
            'CNX': 'Cancelled',
            'GCH': 'Gate changed - Departing {}'.format(peobt),
            'GTO': 'Gate {} open - Departing {}'.format(f['gate'], peobt),
            'GCL': 'Gate {} closing - Departing {}'.format(f['gate'], peobt),
            'GTD': 'Gate closed - Departing {}'.format(peobt),
            'SCH': 'Scheduled',
            'TOM': 'Delayed tomorrow {}'.format(peobt),
            'WIL': 'Wait in lounge. Departing {}'.format(peobt),
        }

        f['flightOutputStatus'] = status_list.get(status, status)

        updated_flight_list.append(f)

    return updated_flight_list


def get_flight_page_count(operation, local_datetime):
    response = get_response(operation, local_datetime)
    link = response.headers['Link']
    page_count = re.findall(r'(?<=page\=)\d+', link)[0]
    return int(page_count)


@format_to_data_table
@merge_codeshare_flights
def get_schiphol_flights(operation, carousel=False):

    if carousel:
        local_datetime = get_local_datetime(max_interval=120, min_interval=60)
    else:
        local_datetime = get_local_datetime()

    flight_list = []
    page_count = get_flight_page_count(operation, local_datetime)
    page = 0

    for page in range(0, page_count + 1):
        response = get_response(operation, local_datetime, page)

        # Check response type
        if response.status_code == 500:
            print('Http 500: API responded with an internal server error.')
            break

        elif response.status_code == 200:
            response_data = response.json()

            # For each flight align keys and values with template.
            flights = update_flight_data(response_data['flights'],
                                         local_datetime)

            if flights and flights[-1] == "Max_time_exceeded":
                break

            flight_list += flights

    # Cache if the flight list is not empty:
    if flight_list:
        cache.set('schipol_{}'.format(operation), flight_list, None)

    return sorted(flight_list, key=itemgetter('scheduledTimestamp', 'city'))


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
