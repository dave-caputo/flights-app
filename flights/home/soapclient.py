import os
import sys
from suds import null, WebFault
from suds.client import Client
import logging

from django.conf.settings import FLIGHTS_KEY


username = 'davecaputo'
apiKey = FLIGHTS_KEY
url = 'http://flightxml.flightaware.com/soap/FlightXML2/wsdl'


logging.basicConfig(level=logging.INFO)
api = Client(url, username=username, password=apiKey)

# Below is testing data only.

# Get the weather
result = api.service.Metar('KAUS')
print(result)

# Get the flights enroute
result = api.service.Enroute('KSMO', 10, '', 0)
flights = result['enroute']

print("Aircraft en route to KSMO:")
for flight in flights:
    print("%s (%s) \t%s (%s)" % (flight['ident'], flight['aircrafttype'],
                                 flight['originName'], flight['origin']))
