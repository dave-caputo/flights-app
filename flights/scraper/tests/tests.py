import os.path
import pickle
import random

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.test import TestCase
from scraper.source.schiphol_source import SchipholFlightManager


class SchipholTest(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations = ['arrivals', 'departures']

    def test_manager_saves_base_data(self):
        for operation in self.operations:

            pkl_prefix = '/scraper/tests/'
            pkl_name = 'sch_base_{}.pickle'.format(operation)
            pkl_path = settings.BASE_DIR + pkl_prefix + pkl_name

            action = 'base'

            # Skip test if a file containing flight data already exists.
            if os.path.isfile(pkl_path):
                print('Schiphol {} {} file already exists.'.format(action, operation))
                continue

            f = SchipholFlightManager(operation)
            f.get_and_save_flight_data(pkl_prefix=pkl_prefix,
                                       action=action)

            with open(pkl_path, 'rb') as p:
                u = pickle.load(p)
            self.assertGreater(len(u), 0)

    def test_manager_sets_start_and_end_pages(self):
        print('\nThis is test 2:')
        for operation in self.operations:
            f = SchipholFlightManager(operation)
            f.str_min_datetime = '16:30'
            f.str_max_datetime = '18:30'
            f.set_start_and_end_page()
            self.assertGreater(f.start_page, 0)
            self.assertGreater(f.end_page, 0)
            print(self.arrivals.str_min_datetime)

    def test_manager_gets_flights_in_range_between_start_and_end_pages(self):
        print('\nThis is test 3:')
        for operation in self.operations:

            action = 'update'
            pkl_prefix = '/scraper/tests/'
            pkl_name = 'sch_{}_{}.pickle'.format(action, operation)
            pkl_path = settings.BASE_DIR + pkl_prefix + pkl_name

            # Skip test if a file containing flight data already exists.
            if os.path.isfile(pkl_path):
                print('Schiphol {} {} file already exists.'.format(action, operation))
                continue

            f = SchipholFlightManager(operation)
            f.str_min_datetime = '16:30'
            f.str_max_datetime = '18:30'
            f.set_start_and_end_page()
            f.get_and_save_flight_data(pkl_prefix=pkl_prefix,
                                       action=action)

            with open(pkl_path, 'rb') as p:
                flight_list = pickle.load(p)
            expected_len = (f.end_page - f.start_page + 1) * 20
            self.assertEqual(len(flight_list), expected_len)

    def test_manager_creates_live_flight_file(self):
        print('\nThis is test 4:')
        for operation in self.operations:
            pkl_prefix = '/scraper/tests/'

            # Base file
            pkl_name1 = 'sch_base_{}.pickle'.format(operation)
            pkl_base = settings.BASE_DIR + pkl_prefix + pkl_name1

            # Live file
            pkl_name2 = 'sch_live_{}.pickle'.format(operation)
            pkl_live = settings.BASE_DIR + pkl_prefix + pkl_name2

            f = SchipholFlightManager(operation)
            f.str_min_datetime = '16:30'
            f.str_max_datetime = '18:30'
            f.set_start_and_end_page()
            f.create_live_flight_file(pkl_prefix=pkl_prefix)

            with open(pkl_base, 'rb') as p:
                base_list = pickle.load(p)

            with open(pkl_live, 'rb') as p:
                live_list = pickle.load(p)

            self.assertEqual(len(base_list), len(live_list))
