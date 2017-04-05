from bs4 import BeautifulSoup
import urllib.request
import re
import requests

from scraper.source.decorators import format_to_data_table


links = {
    'departures': 'http://www.heathrow.com/portal/site/Heathrow/templat'
                  'e.BINARYPORTLET/menuitem.69da03430284b1bcc04fc982d79'
                  '853a0/resource.process/?javax.portlet.tpst=585683456'
                  '7d4493f694e65e4e77b53a0&javax.portlet.rid_5856834567'
                  'd4493f694e65e4e77b53a0=loadInActiveFlights&javax.por'
                  'tlet.rcl_5856834567d4493f694e65e4e77b53a0=cacheLevel'
                  'Page&javax.portlet.begCacheTok=com.vignette.cachetok'
                  'en&javax.portlet.endCacheTok=com.vignette.cachetoken',

    'arrivals': 'http://www.heathrow.com/portal/site/Heathrow/template.'
                'BINARYPORTLET/menuitem.3ba7b9b21f43fd43dca78992d79853a'
                '0/resource.process/?javax.portlet.tpst=c0d0c173a362393'
                'f694e65e4e77b53a0&javax.portlet.rid_c0d0c173a362393f69'
                '4e65e4e77b53a0=loadInActiveFlights&javax.portlet.rcl_c'
                '0d0c173a362393f694e65e4e77b53a0=cacheLevelPage&javax.p'
                'ortlet.begCacheTok=com.vignette.cachetoken&javax.portl'
                'et.endCacheTok=com.vignette.cachetoken',
}


@format_to_data_table
def get_heathrow_flights(operation):
    r = requests.get(links[operation])
    r = r.json()
    flights = r['flightList']
    for item in flights:
        if 'flightStatusTime' not in item:
            item['flightStatusTime'] = ''
    return flights
