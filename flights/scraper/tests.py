from django.core.cache import cache
from django.test import TestCase

from scraper.source.schiphol_source import get_destinations
# from scraper.gatwick_source import testlink, bowlmap, chunkmap
# from scraper.scraper import FlightScraper


'''
f = FlightScraper(testlink, bowlmap, chunkmap)

fields = ['airlineName', 'flightStatusTime', 'city', 'flightNumber',
          'flightStatusText', 'terminalID', 'Gate', 'Notification', 'Pin']

class ScraperTest(TestCase):

    def test_FlightScraper_object_initialized_with_gatwick_source(self):
        self.assertIsInstance(f, FlightScraper)
        # self.assertEqual(f.chunks[0]['Airline'], 'Ryanair')

    def test_gatwick_scraper_builds_test_page_list(self):
        self.assertEqual(len(f.page_list), 1)

    def test_gatwick_scraper_builds_test_block_list(self):
        self.assertTrue(len(f.block_list) >= 100)

    def test_gatwick_scraper_data_list_contains_correct_data(self):
        for i in f.data_list:
            for field in fields:
                self.assertNotEqual(i[field], 'Not Available')
'''


class SchipolTest(TestCase):

    def test_destinations_are_received_and_cached(self):
        d = get_destinations()
        # print(cache.get('destinations'))
        print(d)
        self.assertEqual(cache.get('destinations'), d)
