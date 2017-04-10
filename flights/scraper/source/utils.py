from datetime import datetime, timedelta

import pytz

from django.utils import timezone


def format_to_data_table(func):
    def wrapper(*args, **kwargs):
        return {'data': func(*args, **kwargs)}
    return wrapper


def filter_flight_list(flight_list, operation, min_arrival=30, max_arrival=60,
                       min_departure=40, max_departure=220):
    data = []

    utc_now = timezone.now()
    london_tz = pytz.timezone('Europe/London')
    right_now = utc_now.astimezone(london_tz)

    for i, f in enumerate(flight_list):

        # bound list by scheduled time
        h = datetime.strptime(f['scheduledTimestamp'], '%H:%M')
        d = datetime.combine(right_now.date(), h.time())
        d = london_tz.localize(d)

        if operation == 'arrivals':
            too_early = right_now - d > timedelta(minutes=min_arrival)
            too_late = d - right_now > timedelta(minutes=max_arrival)
        else:
            too_early = d - right_now < timedelta(minutes=min_departure)
            too_late = d - right_now > timedelta(minutes=max_departure)
        if too_early or too_late:
            continue

        # merge flights by city and status
        pf = flight_list[i - 1]
        city_rep = f['city'] == pf['city']
        status_rep = f['flightOutputStatus'] == pf['flightOutputStatus']

        if city_rep and status_rep:
            if data:
                data[-1]['airlineName'] = ''
                data[-1]['flightNumber'] += ', {}'.format(f['flightNumber'])
            continue
        data.append(f)
    return data
