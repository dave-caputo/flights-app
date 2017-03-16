from bs4 import BeautifulSoup
import urllib.request
import re
import requests


links = {
    'departures': 'http://www.heathrow.com/portal/site/Heathrow/template.BINARYPORTLET/menuitem.d1be1e7ae02ef1c9728b08a0d79853a0/resource.process/?javax.portlet.tpst=2c220faf42d1e297fe823291e77b53a0&javax.portlet.rid_2c220faf42d1e297fe823291e77b53a0=loadActiveDepartureFlightsForToday&javax.portlet.rcl_2c220faf42d1e297fe823291e77b53a0=cacheLevelPage&javax.portlet.begCacheTok=com.vignette.cachetoken&javax.portlet.endCacheTok=com.vignette.cachetoken&flightIndex=50',
    'arrivals': 'http://www.heathrow.com/portal/site/Heathrow/template.BINARYPORTLET/menuitem.3ba7b9b21f43fd43dca78992d79853a0/resource.process/?javax.portlet.tpst=c0d0c173a362393f694e65e4e77b53a0&javax.portlet.rid_c0d0c173a362393f694e65e4e77b53a0=loadActiveFlightsForToday&javax.portlet.rcl_c0d0c173a362393f694e65e4e77b53a0=cacheLevelPage&javax.portlet.begCacheTok=com.vignette.cachetoken&javax.portlet.endCacheTok=com.vignette.cachetoken&flightIndex=50',
}


def get_heathrow_flights(operation):
    r = requests.get(links[operation])
    r = r.json()
    return r['flightList']
