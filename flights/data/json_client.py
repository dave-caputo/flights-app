import requests
from requests.auth import HTTPBasicAuth

from django.conf.settings import FLIGHTS_KEY

username = 'davecaputo'
password = FLIGHTS_KEY

# EGLL: Heathrow
# EGKK: Gatwick
# EGSS: Stansted
# EGLC: London City
# EGGW: Luton

flights_url = 'http://flightxml.flightaware.com/json/FlightXML2/'
params = {'airport': 'EGKK', 'howMany': 15, 'filter': '', 'offset': 0}
auth = HTTPBasicAuth(username, password)
r = requests.get(flights_url + 'Enroute', params=params, auth=auth)

with open('tests/enroute.json', 'w') as f:
    f.write(r.text)
