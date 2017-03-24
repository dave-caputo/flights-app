from scraper.scraper import FlightScraper

gatwick_arrivals_test_links = [
    'test',  # Tells FlightScraper that the source are test files and not urls.
    'scraper/source/gatwick_test.html',
]

gatwick_arrivals_test_blockmap = ['tr', {'class_': 'flight-info-row'}]

gatwick_arrivals_test_datamap = [
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


def get_gatwick_flights(operation):
    if operation == 'arrivals':
        r = FlightScraper(gatwick_arrivals_test_links,
                          gatwick_arrivals_test_blockmap,
                          gatwick_arrivals_test_datamap)
        return r.data_list
