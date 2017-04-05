from django.core.cache import cache

from scraper.source.decorators import format_to_data_table
from scraper.scraper import FlightScraper

'''
gatwick_arrivals_test_links = [
    'test',  # Tells FlightScraper that the source are test files and not urls.
    'scraper/source/gatwick_arrivals_test.html',
]

gatwick_departures_test_links = [
    'test',
    'scraper/source/gatwick_departures_test.html',
]
'''

gatwick_arrivals_live_links = [
    'http://www.gatwickairport.com/flights/?type=arrivals'
]

gatwick_departures_live_links = [
    'http://www.gatwickairport.com/flights/?type=departures'
]

gatwick_test_blockmap = ['tr', {'class_': 'flight-info-row'}]

gatwick_test_datamap = [
    {
        'label': 'airlineName',
        'action': 'find attribute',
        'tag': 'td',
        'attribute': 'data-airline-name',
    },


    {
        'labels':
            [
                'airlineName', 'flightStatusTime', 'city', 'flightNumber',
                'flightStatusText', 'terminalId', 'Gate', 'Notification', 'Pin'
            ],  # list must include all columns titles incl. those to be removed.
        'action': 'get_table_columns',
        'remove_column': 1,
        'tag': 'td',
    },
]


@format_to_data_table
def get_gatwick_flights(operation):
    op_links = {
        'arrivals': gatwick_arrivals_live_links,
        'departures': gatwick_departures_live_links}

    r = FlightScraper(op_links[operation],
                      gatwick_test_blockmap,
                      gatwick_test_datamap)

    return r.data_list
