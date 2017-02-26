import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.core.cache import cache

from data import enroute_test
from data.serializer import EnrouteSerializer



# EGLL: Heathrow
# EGKK: Gatwick
# EGSS: Stansted
# EGLC: London City
# EGGW: Luton

OPERATION_MAPPING = {
    'Enroute': {'test_file' : enroute_test,
                'position': ('EnrouteResult', 'enroute')},
}


class FlightClient:
    url = 'http://flightxml.flightaware.com/json/FlightXML2/'
    username = 'davecaputo'
    password = settings.FLIGHTS_KEY
    auth = HTTPBasicAuth(username, password)

    def __init__(self):
        self.request = {}

    def get_live_request(self, operation, params=None):
        '''Make request to FlightAware live flight data.'''
        target = OPERATION_MAPPING[operation]
        pos1, pos2 = target['position']
        
        r = requests.get(
            self.url + operation, params=params, auth=self.auth)
        r = r.json()
        r = r[pos1][pos2]
        
        self.request = r
        cache.set(operation, self.request, None)
        return self.request

    def get_test_request(self, operation):
        '''
        Make request to an existing local test file using a mapping 
        dict to find the flight data.
        '''

        target = OPERATION_MAPPING[operation]
        file = target['test_file']
        pos1, pos2 = target['position']
        self.request = file.flights[pos1][pos2]
        return self.request

    def save(self):
        serializer = EnrouteSerializer(data=self.request, many=True)
        if serializer.is_valid():
            serializer.save()

    def build_test_files(self, operation):
        with open('data/tests/enroute.txt', 'w') as f1:
            f1.write(self.request.text)

        with open('data/enroute_test.py', 'w') as f2:
            f2.write(str(self.request.json()))

