import os.path
import pickle
import random

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.test import TestCase
from scraper.source.schiphol_source import SchipholFlightManager


class SchipholTest(TestCase):

    def test_that_manager_saves_data(self):
        for operation in ['arrivals', 'departures']:

            pkl_file_name = '/scraper/tests/schiphol_{}.pickle'.format(
                operation)

            # Skip test if a file containing flight data already exists.
            if os.path.isfile(settings.BASE_DIR + pkl_file_name):
                print('Schiphol {} file already exists.'.format(operation))
                continue

            f = SchipholFlightManager(operation)
            f.get_and_save_flight_data(test=True)

            with open(pkl_file_name, 'rb') as p:
                u = pickle.load(p)
            self.assertGreater(len(u), 0)

