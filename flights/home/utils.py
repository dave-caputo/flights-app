from datetime import datetime, timedelta

from django.core.cache import cache


def get_enroute_flights():
    all_flights = []
    airports = ('EGLL', 'EGKK')
    for a in airports:
        c = cache.get('enroute_{}'.format(a), 'Not found')
        all_flights += c

    all_flights = sorted(all_flights,
                         key=lambda k: k['estimatedarrivaltime'])

    somedaysago = datetime.now() - timedelta(days=0.5)

    current_flights = []
    for f in all_flights:
        if f['estimatedarrivaltime'] >= int(somedaysago.timestamp()):
            current_flights.append(f)
    return current_flights


def get_arrived_flights():
    all_flights = []
    airports = ('EGLL', 'EGKK')
    for a in airports:
        c = cache.get('arrived_{}'.format(a), [])
        all_flights += c

    all_flights = sorted(all_flights,
                         key=lambda k: k['actualarrivaltime'])
    return all_flights

def get_enroute_arrived_flights():
    a = get_arrived_flights()
    b = get_enroute_flights()
    flights = a + b
    for f in flights:
        f['timesort'] = f.get('estimatedarrivaltime', 0) + \
            f.get('actualarrivaltime', 0)
    flights = sorted(flights, key=lambda k: k['timesort'])
    return flights
