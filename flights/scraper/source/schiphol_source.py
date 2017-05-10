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
    '''
    Provides methods to request flights from API and process data to
    return template-friendly flights lists.
    '''

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
        '''
        Returns the local datetime based on the UTC time and the local
        time zone provided on initialization.
        '''
        utc_datetime = timezone.now()
        local_datetime = utc_datetime.astimezone(self.local_timezone)
        return local_datetime


    def set_time_limits(self, max_minutes=None, min_minutes=None):
        '''
        Sets the maximum and minimum time limits outside which flights
        will not be retrieved.
        '''
        if max_minutes and min_minutes:
            self.max_datetime = self.local_datetime + timedelta(minutes=max_minutes)
            self.min_datetime = self.local_datetime - timedelta(minutes=min_minutes)

            str_time = lambda x: datetime.strftime(x, '%H:%M')
            self.str_max_datetime = str_time(self.max_datetime)
            self.str_min_datetime = str_time(self.min_datetime)


    def make_request(self, page=None, str_time=0):
        '''
        Makes a request to the Schiphol Airport API based on the
        object's url, headers and params. Returns a response object.
        '''
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
        '''
        Translate the scheduled time provided in response as a string,
        to a datetime object.
        '''
        str_scheduled_time = flight['scheduleTime']
        t = datetime.strptime(str_scheduled_time, '%H:%M:%S')
        d = datetime.combine(self.local_datetime.date(), t.time())
        scheduled_datetime = self.local_timezone.localize(d)

        return scheduled_datetime


    def get_city_name(self, flight):
        '''
        Matches the city code in the response to the city name, seeking
        first in the database. If the city name is not found, it will
        get it via make an API request and save the city name to the
        database.
        '''
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
        '''
        For the flight list in the API response, transforms each field
        for processing and displaying correctly the data in the
        template.
        '''
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
        '''
        Makes an API request to obtain from the headers the page count.
        '''
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
        '''
        Returns a template-friendly sorted flight list to display in
        carousel or full list views.
        '''
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
    '''
    Instantiates a SchipolFlightManager object specifying the operation
    and whether the data should be customised for displaying in a
    carousel.
    '''
    m = SchipholFlightManager(operation, carousel)
    flights = m.get_flights()
    return flights
