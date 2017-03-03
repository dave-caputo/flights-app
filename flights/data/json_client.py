import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.core.cache import cache

from data import enroute_test
from data.serializer import EnrouteSerializer

OPERATION_MAPPING = {
    'Enroute': {'test_file': enroute_test,
                'position': ('EnrouteResult', 'enroute')},
}


class FlightClient:
    url = 'http://flightxml.flightaware.com/json/FlightXML2/'
    username = 'davecaputo'
    password = settings.FLIGHTS_KEY
    auth = HTTPBasicAuth(username, password)

    def __init__(self):
        self.request = {}

    def get_live_request(self, operation, params):
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
        mapping = {'Enroute': enroute_test, }
        file = mapping[operation]
        self.request = file.flights[operation + 'Result'][operation.lower()]
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

