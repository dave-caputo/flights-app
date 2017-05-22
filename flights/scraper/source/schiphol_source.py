from datetime import datetime, timedelta
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
        peobt = peobt[11:-13] if peobt else ''

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

        attempt = 0
        valid_response = False

        while not valid_response:
            response = requests.request("GET", self.url, headers=self.headers,
                                        params=self.params)
            print('Page {}: Request status: {}'.format(
                self.params['page'], response.status_code))
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
        return self.total_pages

    def request_flights_in_page(self, page=0):
        '''
        Requests flights in a given page and replaces items retrieved
        with a FormattedFlight object for added functionality. Adds page
        item to the flight.
        '''

        # request flights
        self.params['flightdirection'] = self.operation[0] if self.operation else None
        self.params['page'] = page
        response = self.make_request()
        flights = response.json()['flights']

        # replace flight with FormattedFlight dict-like object and adds
        # page to item.
        for i, f in enumerate(flights):
            ff = FormattedFlight(f).format_flight()
            ff['page'] = page
            flights[i] = ff

        return flights


    def request_flights_in_page_range(self, start_page, end_page):

        all_flights = []
        for page in range(start_page, end_page + 1):
            flights = self.request_flights_in_page(page=page)
            all_flights += flights

        return all_flights



class DtMgr:

    def __init__(self):
        self.utc_dt = datetime.now(tz=pytz.UTC)
        self.ams_tz = pytz.timezone('Europe/Amsterdam')
        self.ams_dt = self.utc_dt.astimezone(self.ams_tz)

    def set_time_limits(self, min_minutes=60, max_minutes=120):
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


    def __init__(self, *args, op='', **kwargs):
        super().__init__(*args, **kwargs)
        self.operation = op
        self.pkl_path = None
        self.dt = None
        self.start_index = None


    def set_file_path(self, action):
        dt = DtMgr()
        ams_dt = dt.ams_dt.strftime('%y%m%d')
        pkl_name = 'sch_{}_{}_{}.pickle'.format(action, self.operation, ams_dt)
        self.pkl_path = settings.BASE_DIR + '/scraper/source/files/' + pkl_name


    def save_to_file(self, action):
        flights = {'flist': self, 'flist_dt': self.dt}
        self.set_file_path(action)
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


    def load_from_file(self, action):
        self.set_file_path(action)
        with open(self.pkl_path, 'rb') as pkl:
            flights = pickle.load(pkl)
            self.extend(flights['flist'])
            self.dt = flights['flist_dt']
        print('Schiphol: Flight list loaded from file.')


    def get_from_API(self, start_page=0, end_page=None):
        '''
        Makes a request using a SchClient instance and adds items to the
        FlightList if no start/end pages are provided. Otherwise, it
        only returns the flights from the page range.
        '''

        # Request flights from API.
        r = SchClient(self.operation)
        end_page = end_page if end_page else r.total_pages

        flights = r.request_flights_in_page_range(start_page, end_page)

        # Set a timedate for the FlightList.
        self.dt = DtMgr().ams_dt.replace(microsecond=0)
        print('FlightList datetime set at: {}'.format(self.dt))

        # If page range is given self will not be updated.
        if start_page and end_page:
            return flights
        else:
            # First, delete any items in the FlightList if any.
            for item in self:
                del item

            # Add all items retrieved from API.
            self.extend(flights)


    def get_page_range(self, start_dt, end_dt):
        for item in self:
            if start_dt <= item['scheduleDatetime'][:-3]:
                start = item['page']
                print('Start page dt: {}'.format(item['scheduleDatetime'][:-3]))
                break
        for item in reversed(self):
            if end_dt >= item['scheduleDatetime'][:-3]:
                end = item['page']
                print('End page dt: {}'.format(item['scheduleDatetime'][:-3]))
                break

        return start, end


    def get_start_index(self):
        for index, item in enumerate(self):
            current_dt = datetime.strftime(DtMgr().ams_dt, '%Y-%m-%d %H:%M:%S')
            if item['scheduleDatetime'] >= current_dt:
                self.start_index = index
                return index


    def update_list(self):
        '''
        Makes API request for a range of pages based on the set timelimits,
        and replaces items in the FlightList instance with the updated ones.
        '''

        dt = DtMgr()
        lmts = dt.set_time_limits()
        start_page, end_page = self.get_page_range(lmts['str_min_dt'], lmts['str_max_dt'])
        print('Page range obtained:\n'
              '> Start page: {}.\n'
              '> End page:{}.'.format(start_page, end_page))
        updated_flights = self.get_from_API(start_page=start_page, end_page=end_page)
        for i, flight in enumerate(self):
            for updated_flight in updated_flights:
                if flight['id'] == updated_flight['id']:
                    self[i] = updated_flight


@format_to_data_table
def format_to_render(flight_list, operation):

    render_list = FlightList(op=operation)
    render_list.dt = flight_list.dt

    for f in flight_list:
        if f['flightName'] == f['mainFlight'] and f['serviceType'] == "J":
            render_list.append(f)

    render_list.get_start_index()

    return render_list


def get_schiphol_flights(operation):
    flights = FlightList(op=operation)
    flights.set_file_path('base')
    if os.path.isfile(flights.pkl_path):
        flights.load_from_file('base')
        flights.get_start_index()

        dt = DtMgr()
        fdt = dt.convert_to_ams_tz(flights.dt + timedelta(minutes=5))
        print('Next refresh: {}'.format(fdt))
        print('Current time: {}'.format(dt.ams_dt))
        print('Start index set at: {}'.format(flights.start_index))

        if dt.ams_dt > fdt:
            flights.update_list()
            flights.save_to_file('base')
    else:
        flights.get_from_API()
        flights.get_start_index()
        flights.save_to_file('base')

    flights = format_to_render(flights, operation)
    return flights
