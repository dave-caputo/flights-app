from datetime import datetime, timedelta

from django.core.cache import cache

# Decorators:

def crop_request(func):
    def wrapper(self, operation, *args, **kwargs):
        r = func(self, operation, *args, **kwargs)

        mapping = {'Arrived': 'arrivals', 'Departed': 'departures'}

        if operation in mapping:
            op = mapping[operation]
        else:
            op = operation.lower()
        try:
            r = r[operation + 'Result'][op]
            self.data = r
            return r
        except:
            return r
    return wrapper


def cache_operation(func):
    def wrapper(self, operation, *args, **kwargs):
        r = func(self, operation, *args, **kwargs)
        if type(r) != str:
            try:
                airport = args[0]['airport']
            except:
                pass
            cache.set('{}_{}'.format(operation.lower(), airport), r, None)
            return r
        return r
    return wrapper

# Helper functions:

def get_enroute_flights():
    all_flights = []
    airports = ('EGLL', 'EGKK')
    for a in airports:
        c = cache.get('enroute_{}'.format(a), 'Not found')
        all_flights += c

    all_flights = sorted(all_flights,
                         key=lambda k: k['estimatedarrivaltime'])

    somedaysago = datetime.now() - timedelta(days=2)

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

def get_scheduled_flights():
    all_flights = []
    airports = ('EGLL', 'EGKK')
    for a in airports:
        c = cache.get('scheduled_{}'.format(a), [])
        all_flights += c

    all_flights = sorted(all_flights,
                         key=lambda k: k['filed_departuretime'])
    return all_flights

def get_departed_flights():
    all_flights = []
    airports = ('EGLL', 'EGKK')
    for a in airports:
        c = cache.get('departed_{}'.format(a), [])
        all_flights += c

    all_flights = sorted(all_flights,
                         key=lambda k: k['actualdeparturetime'])
    return all_flights

def get_scheduled_departed_flights():
    a = get_departed_flights()
    b = get_scheduled_flights()
    flights = a + b
    for f in flights:
        f['timesort'] = f.get('actualdeparturetime', 0) + \
            f.get('filed_departuretime', 0)
    flights = sorted(flights, key=lambda k: k['timesort'])
    return flights
