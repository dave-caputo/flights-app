from datetime import datetime, timedelta
import logging
import pickle
import pytz
import os
import random
import re
import requests
import sys

from django.conf import settings
from scraper.source.utils import format_to_data_table, filter_flight_list
from cities.models import City



logger = logging.getLogger(__name__)



class FormattedFlight(dict):

    def format_flight(self):
        self.add_items()
        self.translate_status()
        return self

    def add_items(self):

        # Key aligned with template and 'seconds' info sliced off.
        self['scheduleDatetime'] = self['scheduleDate'] + ' ' + self['scheduleTime']
        self['scheduledTimestamp'] = self['scheduleTime'][:-3]

        codeshares = 'Codeshares: ' + ", ".join(self['codeshares']['codeshares']) if self['codeshares'] else ''
        self['flightNumber'] = '{}<p>{}</p>'.format(self['mainFlight'], codeshares)

        self['terminalId'] = self['terminal']

        city_codes = self['route']['destinations']
        for i, code in enumerate(city_codes):
            try:
                city_codes[i] = City.objects.get(iata=code).city
            except:
                continue
        self['city'] = ", ".join(city_codes)


    def translate_status(self):
        status = self['publicFlightState']['flightStates']
        status = status[0] if len(status) > 0 else 'NAV'

        elt = self['estimatedLandingTime']
        elt = elt[11:-13] if elt else self['scheduledTimestamp']


        alt = self['actualLandingTime']
        alt = alt[11:-13] if alt else self['scheduledTimestamp']

        peobt = self['publicEstimatedOffBlockTime']
        peobt = peobt[11:-13] if peobt is not None else ''

        aobt = self['actualOffBlockTime']
        aobt = aobt[11:-13] if aobt else ''

        status_codes = {
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
            'GTO': 'Gate {} open - Departing {}'.format(self['gate'], peobt),
            'GCL': 'Gate {} closing - Departing {}'.format(self['gate'], peobt),
            'GTD': 'Gate closed - Departing {}'.format(peobt),
            'SCH': 'Scheduled',
            'TOM': 'Delayed tomorrow {}'.format(peobt),
            'WIL': 'Wait in lounge. Departing {}'.format(peobt),

            'NAV': 'Not available'
        }

        self['flightOutputStatus'] = status_codes.get(status)



class SchClient(object):

    def __init__(self, op=''):
        self.url = 'https://api.schiphol.nl/public-flights/flights'
        self.headers = {'resourceversion': 'v3'}
        self.params = {
            'app_id': '7e07d59a',
            'app_key': '144051ede9ab257ce820328c024c94dc',
            'flightdirection': None,
            'includedelays': False,
            'page': 0,
            'scheduletime': None,
            'sort': '+scheduleTime'  # No other filters available: API bug!
        }
        self.max_request_attempts = 30
        self.operation = op
        self.total_pages = None
        self.get_total_pages()
        print('Total pages: {}'.format(self.total_pages))


    def make_request(self):
        print('Making request...')
        attempt = 0
        valid_response = False

        while not valid_response:
            response = requests.request("GET", self.url, headers=self.headers,
                                        params=self.params)
            print('Request status: {}'.format(response.status_code))
            if response.status_code == 200 or response.status_code == 204:
                valid_response = True
            attempt += 1
            if attempt == self.max_request_attempts:
                raise ConnectionError
        print('Response obtained after {} attempt{}.'.format(
            attempt, '' if attempt == 1 else 's'))
        return response

    def get_total_pages(self):
        '''
        Gets the total number of pages available for request for the
        operation.
        '''

        print('Getting total pages...')
        self.params['flightdirection'] = self.operation[0] if self.operation else None
        response = self.make_request()
        link = response.headers['Link']
        self.total_pages = int(re.findall(r'(?<=page\=)\d+', link)[0])


    def request_flights_in_page(self, page=0):
        '''
        Requests flights in a given page and replaces items retrieved
        with a FormattedFlight object for added functionality. Adds page
        item to the flight.
        '''

        # request flights
        print('Request to be sent for page {}...'.format(page))
        self.params['flightdirection'] = self.operation[0] if self.operation else None
        self.params['page'] = page
        response = self.make_request()
        if response.status_code == 204:
            return []

        flights = response.json()['flights']

        # replace flight with FormattedFlight dict-like object and adds
        # page to item.
        for i, f in enumerate(flights):
            ff = FormattedFlight(f).format_flight()
            ff['page'] = page
            flights[i] = ff
        print('{} flights were obtained and formatted!'.format(len(flights)))
        return flights


    def request_flights_in_page_range(self, start_page, end_page):
        print('Requesting flights in page range...')
        all_flights = []
        for page in range(start_page, end_page + 1):
            flights = self.request_flights_in_page(page=page)
            all_flights += flights
        print('{} flights obtained from page range!'.format(len(all_flights)))

        return all_flights



class DtMgr:

    def __init__(self):
        print('Initializing Datetime Manager...')
        self.utc_dt = datetime.now(tz=pytz.UTC)
        self.ams_tz = pytz.timezone('Europe/Amsterdam')
        self.ams_dt = self.utc_dt.astimezone(self.ams_tz)
        print('Current time in Amsterdam: {}'.format(self.ams_dt))
        print('Datetime Manager initialized!')
        self.file_dt = None

    def set_time_limits(self, min_minutes=60, max_minutes=60):
        if max_minutes and min_minutes:
            limits = {}

            limits['max_dt'] = self.ams_dt + timedelta(minutes=max_minutes)
            limits['min_dt'] = self.ams_dt - timedelta(minutes=min_minutes)

            str_dt = lambda x: datetime.strftime(x, '%Y-%m-%d %H:%M:%S')

            limits['str_max_dt'] = str_dt(limits['max_dt'])
            limits['str_min_dt'] = str_dt(limits['min_dt'])

            return limits


    def convert_to_ams_tz(self, dt):
        return dt.astimezone(self.ams_tz)




class FlightList(list):


    def __init__(self, *args, op='', pkl='base', **kwargs):
        super().__init__(*args, **kwargs)
        self.operation = op
        self.pkl_path = self.set_pkl_path(pkl)
        self.dt = DtMgr()
        self.cf_index = None  # index of current flight in Ams time.

    def set_pkl_path(self, pkl):
        dt = DtMgr()
        ams_dt = dt.ams_dt.strftime('%y%m%d')
        pkl_name = 'sch_{}_{}_{}.pickle'.format(pkl, self.operation, ams_dt)
        self.pkl_path = settings.BASE_DIR + '/scraper/source/files/' + pkl_name
        logger.info('Pkl path = {}'.format(self.pkl_path))


    def save_to_file(self, action):
        flights = {'flist': self, 'flist_dt': self.dt}
        self.set_pkl_path(action)
        with open(self.pkl_path, 'w'):
            pass  # Clears file contents
        with open(self.pkl_path, 'wb') as pkl:
            pickle.dump(flights, pkl)
        print('Schiphol: Flight list saved to file.')


    def get_file_size(self):
        if os.path.isfile(self.pkl_path):
            kbsize = sys.getsizeof(self.pkl_path) / 1000
            kbsize = round(kbsize, 1)
            return kbsize
        print('No file was found.')


    def load_from_file(self):
        '''
        Deletes any existing items in the FlightList instance, and then
        extends it with a list obtained from the pickle file. If the
        file is not found, the instance remains empty and error is
        logged.
        '''

        logger.info('Loading flights from file...')

        # First delete any existing items from the FlightList instance.
        for item in self:
            del item

        try:
            with open(self.pkl_path, 'rb') as pkl:
                flights = pickle.load(pkl)

            self.extend(flights['flist'])
            logger.info('{} flights loaded from file!'.format(len(self)))

            self.dt = flights['flist_dt']
            logger.info('FlightList datetime = {}!'.format(self.dt.file_dt))

            self.set_cf_index()

        except TypeError:
            logger.error('Oops, a pkl file was not found!')




    def get_from_API(self, start_page=0, end_page=None):
        '''
        Makes a request using a SchClient instance and adds items to the
        FlightList if no start/end pages are provided. Otherwise, it
        only returns the flights from the page range.
        '''

        print('Getting flights from API...')

        # Request flights from API.
        r = SchClient(self.operation)
        end_page = end_page if end_page is not None else r.total_pages

        flights = r.request_flights_in_page_range(start_page, end_page)
        print('Flights obtained via API = {}...'.format(len(flights)))

        # Set a timedate for the FlightList.
        self.dt = DtMgr().ams_dt.replace(microsecond=0)
        print('FlightList datetime = {}'.format(self.dt))

        # If page range is given self will not be updated.
        if start_page is not 0 and end_page is not r.total_pages:
            return flights
        else:
            # First, delete any items in the FlightList if any.
            for item in self:
                del item

            # Add all items retrieved from API.
            self.extend(flights)


    def get_page_range(self, start_dt, end_dt):

        print('Getting page range from start and end datetime...')
        start_page = None
        end_page = None

        for item in self:
            if start_dt <= item['scheduleDatetime'][:-3]:
                start_page = item['page']
                print('Start page dt: {}'.format(item['scheduleDatetime'][:-3]))
                break
        for item in self:
            if end_dt >= item['scheduleDatetime'][:-3]:
                end_page = item['page']
                print('End page dt: {}'.format(item['scheduleDatetime'][:-3]))
                break

        if start_page is not None and end_page is None:
            end_page = self[-1]['page']
        if end_page is not None and start_page is None:
            start_page = 0
        print('>Start page: {}\n>End page: {}'.format(start_page, end_page))
        return start_page, end_page


    def set_cf_index(self):
        '''
        Gets the index of the flight in the FlightList scheduled at the
        current Amsterdam time. This index will be used as a display
        setting in the table rendered in template
        '''

        logger.info('Setting current flight index...')

        for index, item in enumerate(self):
            current_dt = datetime.strftime(DtMgr().ams_dt, '%Y-%m-%d %H:%M:%S')
            if item['scheduleDatetime'] >= current_dt:
                self.cf_index = index
                return index
        logger.info('Current flight index set at {}!'.format(self.dt))


    def update_list(self):
        '''
        Makes API request for a range of pages based on the set timelimits,
        and replaces items in the FlightList instance with the updated ones.
        '''

        lmts = self.dt.set_time_limits()
        start_page, end_page = self.get_page_range(lmts['str_min_dt'], lmts['str_max_dt'])

        if start_page is None and end_page is None:
            print('Nothing to update')
        else:
            updated_flights = self.get_from_API(start_page=start_page, end_page=end_page)
            if updated_flights is None:
                print('No updated flights.')
            else:
                for i, flight in enumerate(self):
                    for updated_flight in updated_flights:
                        if flight['id'] == updated_flight['id']:
                            self[i] = updated_flight
                            print('Flight {} replaced'.format(updated_flight['id']))


@format_to_data_table
def format_to_render(flight_list, operation):

    render_list = FlightList(op=operation)
    render_list.dt = flight_list.dt

    for f in flight_list:
        if f['flightName'] == f['mainFlight'] and f['serviceType'] == "J":
            render_list.append(f)

    render_list.set_cf_index()

    return render_list

def update_is_required(self):
    '''
    Returns True if the datetime of the list loaded from pkl file is
    older than 4 minutes. Otherwise will return False.
    '''
    current_time = self.dt.ams_time
    refresh_time = self.dt.convert_to_ams_tz(self.dt.file_dt + timedelta(
        minutes=4))

    if current_time > refresh_time:
        return True

    return False



def retrieve_schiphol_flights(operation):
    flights = FlightList(op=operation)
    flights.load_from_file()

    if flights and self.update_is_required():
            flights.update_list()
            flights.save_to_file('base')
    #     else:
    #         print('FlightList doesn\'t need to be refreshed yet!')
    else:
        flights.get_from_API()
        flights.set_cf_index()
        flights.save_to_file('base')

    # flights = format_to_render(flights, operation)
    # return flights

def get_schiphol_flights(operation):
    flights = FlightList(op=operation)
    flights.set_pkl_path('base')
    flights.load_from_file('base')
    flights.set_cf_index()

    flights = format_to_render(flights, operation)
    return flights

def test_celery():
    msg = 'Hiya! I\'m a periodic task!'
    print(msg)
    return msg
