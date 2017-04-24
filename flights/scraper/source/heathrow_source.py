from operator import itemgetter

from bs4 import BeautifulSoup
import urllib.request
import re
import requests

from scraper.source.utils import format_to_data_table, filter_flight_list


links = {
    'departures': 'http://www.heathrow.com/portal/site/Heathrow/templat'
                  'e.BINARYPORTLET/menuitem.69da03430284b1bcc04fc982d79'
                  '853a0/resource.process/?javax.portlet.tpst=585683456'
                  '7d4493f694e65e4e77b53a0&javax.portlet.rid_5856834567'
                  'd4493f694e65e4e77b53a0=loadActiveFlightsForToday&jav'
                  'ax.portlet.rcl_5856834567d4493f694e65e4e77b53a0=cach'
                  'eLevelPage&javax.portlet.begCacheTok=com.vignette.ca'
                  'chetoken&javax.portlet.endCacheTok=com.vignette.cach'
                  'etoken',

    'arrivals': 'http://www.heathrow.com/portal/site/Heathrow/template.'
                'BINARYPORTLET/menuitem.3ba7b9b21f43fd43dca78992d79853a'
                '0/resource.process/?javax.portlet.tpst=c0d0c173a362393'
                'f694e65e4e77b53a0&javax.portlet.rid_c0d0c173a362393f69'
                '4e65e4e77b53a0=loadActiveFlightsForToday&javax.portlet'
                '.rcl_c0d0c173a362393f694e65e4e77b53a0=cacheLevelPage&j'
                'avax.portlet.begCacheTok=com.vignette.cachetoken&javax'
                '.portlet.endCacheTok=com.vignette.cachetoken'
}


@format_to_data_table
def get_heathrow_flights(operation, carousel=False):

    #    utc_now = timezone.now()
    #    london_tz = pytz.timezone('Europe/London')
    #    right_now = utc_now.astimezone(london_tz)

    r = requests.get(links[operation])
    r = r.json()
    flight_list = sorted(
        r['flightList'], key=itemgetter('scheduledTimestamp', 'city'))

    data = filter_flight_list(flight_list, operation)
    #    data = []
    #
    #    for i, f in enumerate(flight_list):
    #        # crop list by scheduled time
    #        h = datetime.strptime(f['scheduledTimestamp'], '%H:%M')
    #        d = datetime.combine(right_now.date(), h.time())
    #        d = london_tz.localize(d)
    #
    #        if operation == 'arrivals':
    #            too_early = right_now - d > timedelta(minutes=30)
    #            too_late = d - right_now > timedelta(hours=1)
    #        else:
    #            too_early = d - right_now < timedelta(minutes=40)
    #            too_late = d - right_now > timedelta(minutes=220)
    #        if too_early or too_late:
    #            continue
    #
    #        # merge flights by city and status
    #        pf = flight_list[i - 1]
    #        city_rep = f['city'] == pf['city']
    #        status_rep = f['flightOutputStatus'] == pf['flightOutputStatus']
    #
    #        if city_rep and status_rep:
    #            data[-1]['airlineName'] = ''
    #            data[-1]['flightNumber'] += ', {}'.format(f['flightNumber'])
    #            continue
    #        data.append(f)
    return data
