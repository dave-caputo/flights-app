from datetime import datetime, timedelta
from operator import itemgetter
import re
import requests
import sys

import pytz

from django.conf import settings
from django.core.cache import cache

from django.utils import timezone

from cities.models import City
from cities.utils import SchipholCityManager
from scraper.source.utils import format_to_data_table, merge_codeshare_flights



class SchipholFlightManager:

    def __init__(self, operation, carousel):
        self.operation = operation
        self.carousel = carousel
        self.local_timezone = pytz.timezone('Europe/Amsterdam')
        self.local_datetime = self.get_local_datetime()
        self.time_limits = False
        self.max_datetime = None
        self.str_max_datetime = None
        self.min_datetime = None
        self.str_min_datetime = None
        self.url = 'https://api.schiphol.nl/public-flights/flights'
        self.headers = {'resourceversion': 'v3'}
        self.params = {
            'app_id': '7e07d59a',
            'app_key': settings.SCHIPHOL_KEY,
            'includedelays': True,
            'scheduletime': None,
            'sort': '+scheduleTime'  # No more filters available: API bug!
        }
        self.max_request_attempts = 30


    def get_local_datetime(self):
        utc_datetime = timezone.now()
        local_datetime = utc_datetime.astimezone(self.local_timezone)
        return local_datetime


    def set_time_limits(self, max_minutes=None, min_minutes=None):
        if max_minutes and min_minutes:
            self.max_datetime = self.local_datetime + timedelta(minutes=max_minutes)
            self.min_datetime = self.local_datetime - timedelta(minutes=min_minutes)

            str_time = lambda x: datetime.strftime(x, '%H:%M')
            self.str_max_datetime = str_time(self.max_datetime)
            self.str_min_datetime = str_time(self.min_datetime)


    def make_request(self, page=None, str_time=0):
        attempt = 0
        valid_response = False

        url = self.url
        headers = self.headers
        params = self.params

        params['flightdirection'] = self.operation[0].upper()
        params['page'] = page
        params['scheduleTime'] = str_time

        while not valid_response:
            response = requests.request("GET", url, headers=headers,
                                        params=params)
            print('Flights: Page: {}, Request status: {}'.format(page, response.status_code))
            if response.status_code == 200:
                valid_response = True
            attempt += 1
            if attempt == self.max_request_attempts:
                raise ConnectionError
        print('Response returned. Attempts made: {}'.format(attempt))
        return response


    def get_scheduled_datetime(self, flight):

        str_scheduled_time = flight['scheduleTime']
        t = datetime.strptime(str_scheduled_time, '%H:%M:%S')
        d = datetime.combine(self.local_datetime.date(), t.time())
        scheduled_datetime = self.local_timezone.localize(d)

        return scheduled_datetime


    def get_city_name(self, flight):
        print('Retrieving city name...')

        mgr = SchipholCityManager()
        print('City manager initialized...')

        # Translate city code to city name.
        route = flight['route']
        city_code = route['destinations'][0]
        try:
            print('Finding match in db for {}...'.format(city_code))
            city = City.objects.get(iata=city_code).city
            print('Match found in db!: {}'.format(city))
        except:
            print('{} not found in db. Requesting via API...'.format(city_code))
            city = mgr.get_and_save_city(iata=city_code)
        return city


    def update_flight_data(self, flight_list):
        print('Updating data...')

        updated_flight_list = []

        for f in flight_list:

            # Check flights are within time limits
            if self.time_limits:
                print('Time limits identified')
                scheduled_datetime = self.get_scheduled_datetime(f)
                if scheduled_datetime < self.min_time:
                    continue
                if scheduled_datetime > self.max_time:
                    break
            else:
                print('No time limits identified')

            # Consider only Passenger Line services
            if f['serviceType'] != "J":
                print('Service type {} ignored.'.format(f['serviceType']))
                continue
            else:
                print('Found valid service type: {}'.format(f['serviceType']))

            # Key aligned with template and 'seconds' info sliced off.
            f['scheduledTimestamp'] = f.pop('scheduleTime')[:-3]

            f['city'] = self.get_city_name(f)
            print('City name successfully retrieved')

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


    def get_page_count(self):

        response = self.make_request()

        # Obtain from headers and cache the number of pages
        link = response.headers['Link']
        str_page_count = re.findall(r'(?<=page\=)\d+', link)[0]
        page_count = int(str_page_count)
        print('Page count successfully retrieved: {}'.format(page_count))

        return page_count


    @format_to_data_table
    @merge_codeshare_flights
    def get_flights(self):

        if self.carousel:
            self.set_time_limits(max_minutes=120, min_minutes=60)

        flight_list = []
        page_count = self.get_page_count()
        # page_count = 10
        # page = 0

        for page in range(0, page_count + 1):
            response = self.make_request(page=page,
                                         str_time=self.str_min_datetime)
            data = response.json()
            data = data['flights']
            print('Data obtained for page {}'.format(page))

            # For each flight align keys and values with template.
            flights = self.update_flight_data(data)

            if flights and flights[-1] == "Max_time_exceeded":
                break

            flight_list += flights

        return sorted(flight_list, key=itemgetter('scheduledTimestamp', 'city'))



def get_schiphol_flights(operation, carousel=False):
    m = SchipholFlightManager(operation, carousel)
    flights = m.get_flights()
    return flights




'''
def update_flight_data(flights, local_datetime):

    # destinations = cache.get('destinations')
    pages_cached = cache.get('dest_pages_cached')
    cache_block_size = 20
    updated_flight_list = []

    city_mgr = SchipholCityManager()

    for f in flights:

        str_scheduled_time = f['scheduleTime']
        t = datetime.strptime(str_scheduled_time, '%H:%M:%S')
        d = datetime.combine(local_datetime['now'].date(), t.time())
        scheduled_datetime = local_datetime['tz'].localize(d)

        if local_datetime['time_limits']:

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
            f['city'] = City.objects.get(iata=city_code).city
        except:
            f['city'] = city_mgr.get_and_save_city(iata=city_code)
        """
        try:
            for block in range(20, pages_cached + 1, cache_block_size):
                first = cache.get('dest_{}_start'.format(block))
                print(first)
                last = cache.get('dest_{}_end'.format(block))

                if city_code >= first and city_code <= last:
                    block_data = cache.get('dest_{}'.format(block))

                    f['city'] = (
                        dest['city'] for dest in block_data if dest['iata'] == city_code
                    ).__next__()
        except StopIteration:

            f['city'] = 'Not Available'
        """
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
        cache.set('schiphol_{}'.format(operation), flight_list)

    return sorted(flight_list, key=itemgetter('scheduledTimestamp', 'city'))


def get_response(operation, local_datetime, page=0):

    # More info at https://developer.schiphol.nl/apis/flight-api/flights
    url = 'https://api.schiphol.nl/public-flights/flights'
    p = {
        'app_id': '7e07d59a',
        'app_key': settings.SCHIPHOL_KEY,
        'flightdirection': operation[0].upper(),
        'includedelays': 'true',
        'page': page,
        'scheduletime': local_datetime.get('str_min_time', None),
        'sort': '+scheduleTime'  # No more filters available: API bug!
    }
    h = {'resourceversion': 'v3'}
    try:
        response = requests.request("GET", url, headers=h, params=p)
        return response
    except requests.exceptions.ConnectionError as error:
        print('Unable to get data from page {}'.format(page))
'''
'''
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
'''

'''
def get_destinations():

    url = 'https://api.schiphol.nl/public-flights/destinations'
    p = {
        'app_id': '7e07d59a',
        'app_key': settings.SCHIPHOL_KEY,
        'sort': '+iata'
    }
    h = {
        'resourceversion': 'v1'
    }

    response = requests.request("GET", url, headers=h, params=p)
    if response.status_code == 200:

        # Obtain from headers and cache the number of pages
        link = response.headers['Link']
        page_count = int(re.findall(r'(?<=page\=)\d+', link)[0])
        cache.set('dest_page_count', page_count)
        print('Page count obtained and cached: {}'.format(cache.get('dest_page_count')))

        # Set how data will be cached
        page_block = []
        page_block_size = 20

        for page in range(1, page_count + 1):

            # Include page as a request parameters
            p['page'] = page

            # Retry until response status code 200
            attempt = 0
            valid_response = False
            while not valid_response:
                response = requests.request("GET", url, headers=h, params=p)
                print(response)
                if response.status_code == 200:
                    valid_response = True
                attempt += 1
                if attempt == 30:
                    continue

            d = response.json()

            updated_dest = []
            for item in d['destinations']:
                u = {'iata': item['iata'], 'city': item['city']}
                updated_dest.append(u)

            page_block += updated_dest

            if page % page_block_size == 0 or page == page_count:

                # Set up cache key names
                key = 'dest_{}'.format(page)
                timestamp_key = key + '_timestamp'
                start_key = key + '_start'
                end_key = key + '_end'

                s = page_block[0]['iata']
                if not s:
                    s = 'ZZZ'

                e = page_block[-1]['iata']
                if not e:
                    e = 'ZZZ'

                # Set cache values
                cache.set(key, page_block)
                cache.set(timestamp_key, timezone.now())
                cache.set(start_key, )
                cache.set(end_key, page_block[-1]['iata'])

                cache.set('dest_pages_cached', page)

                msg = 'Page {}: {} destinations were cached.'
                print(msg.format(page, len(page_block)))
                print('Block start: {}. End:{}.'.format(cache.get(start_key), cache.get(end_key)))

                page_block = []

        return 'Destinations successfully cached'
    else:
        print(response)
'''
