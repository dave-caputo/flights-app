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

    def test_manager_saves_data(self):
        for operation in self.operations:

            pkl_file_name = 'scraper/tests/schiphol_{}.pickle'.format(
                operation)
            pkl_file_path = settings.BASE_DIR + '/' + pkl_file_name

            # Skip test if a file containing flight data already exists.
            if os.path.isfile(pkl_file_path):
                print('Schiphol {} file already exists.'.format(operation))
                continue

            f = SchipholFlightManager(operation)
            f.get_and_save_flight_data(test=True)

            with open(pkl_file_path, 'rb') as p:
                u = pickle.load(p)
            self.assertGreater(len(u), 0)

    def test_manager_sets_start_and_end_pages(self):
        for operation in self.operations:
            f = SchipholFlightManager(operation)
            f.str_min_datetime = '16:30'
            f.str_max_datetime = '18:30'
            f.set_start_and_end_page()
            self.assertGreater(f.start_page, 0)
            self.assertGreater(f.end_page, 0)

    def test_manager_gets_flights_in_range_between_start_and_end_pages(self):
        for operation in self.operations:

            pkl_file_name = 'scraper/tests/updated_{}.pickle'.format(operation)
            pkl_file_path = settings.BASE_DIR + '/' + pkl_file_name

            # Skip test if a file containing flight data already exists.
            if os.path.isfile(pkl_file_path):
                print('Schiphol {} file already exists.'.format(operation))
                continue

            f = SchipholFlightManager(operation)
            f.str_min_datetime = '16:30'
            f.str_max_datetime = '18:30'
            f.set_start_and_end_page()
            f.get_and_save_flight_data(test=True, update=True)

            with open(pkl_file_path, 'rb') as p:
                flight_list = pickle.load(p)
            self.assertEqual(len(flight_list), (f.end_page - f.start_page + 1) * 20)
