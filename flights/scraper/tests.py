import random

from django.core.cache import cache
from django.db import transaction
from django.test import TestCase
from scraper.source.schiphol_source import SchipholFlightManager


class SchipholTest(TestCase):

    def test_that_basic_flight_data_is_cached(self):
        operation = random.choice(['arrivals', 'departures'])
        f = SchipholFlightManager(operation)
        try:
            with transaction.atomic:
                flight_list = f.get_and_cache_flight_data(page_count=30)
        except transaction.TransactionManagementError:
            pass

        flight_list = cache.get('schiphol_{}'.format(operation))

        self.assertGreater(len(flight_list), 0)
