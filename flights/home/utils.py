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

    somedaysago = datetime.now() - timedelta(days=3)

    current_flights = []
    for f in all_flights:
        if f['estimatedarrivaltime'] >= int(somedaysago.timestamp()):
            current_flights.append(f)
    return current_flights
