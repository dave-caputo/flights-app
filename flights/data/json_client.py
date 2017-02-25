import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings


# EGLL: Heathrow
# EGKK: Gatwick
# EGSS: Stansted
# EGLC: London City
# EGGW: Luton


class FlightClient:
    url = 'http://flightxml.flightaware.com/json/FlightXML2/'
    username = 'davecaputo'
    password = settings.FLIGHTS_KEY
    auth = HTTPBasicAuth(username, password)

    def __init__(self, operation, params=None):
        self.request = requests.get(
            self.url + operation, params=params, auth=self.auth)

    def build_test_files(self, operation):
        with open('data/tests/enroute.txt', 'w') as f1:
            f1.write(self.request.text)

        with open('data/enroute_test.py', 'w') as f2:
            f2.write(str(self.request.json()))
