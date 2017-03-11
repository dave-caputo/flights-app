import importlib
import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings
from data.serializer import EnrouteSerializer
from data.utils import cache_operation, crop_request


class FlightClient:
    url = 'http://flightxml.flightaware.com/json/FlightXML2/'
    username = 'davecaputo'
    password = settings.FLIGHTS_KEY
    auth = HTTPBasicAuth(username, password)

    @cache_operation
    @crop_request
    def get_live_request(self, operation, params):
        try:
            r = requests.get(
                self.url + operation, params=params, auth=self.auth)
            self.request = r.json()
            print(self.request)
            return self.request
        except:
            return 'Live request failed'

    @crop_request
    def get_test_request(self, operation):
        test_file_name = 'data.{}_test'.format(operation.lower())
        test_file = importlib.import_module(test_file_name)
        self.request = test_file.flights
        return self.request

    '''
    def save(self):
        serializer = EnrouteSerializer(data=self.request, many=True)
        if serializer.is_valid():
            serializer.save()

    def build_test_files(self, operation):
        with open('data/tests/enroute.txt', 'w') as f1:
            f1.write(self.request.text)

        with open('data/enroute_test.py', 'w') as f2:
            f2.write(str(self.request.json()))
    '''
