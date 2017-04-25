import re

import requests

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def get_Schiphol_cities():

    url = 'https://api.schiphol.nl/public-flights/destinations'
    p = {
        'app_id': '7e07d59a',
        'app_key': settings.SCHIPHOL_KEY,
        'sort': '+iata'
    }
    h = {
        'resourceversion': 'v1'
    }

    response = requests.request("GET", url, headers=h, params=p)
    if response.status_code == 200:

        # Obtain from headers and cache the number of pages
        link = response.headers['Link']
        page_count = int(re.findall(r'(?<=page\=)\d+', link)[0])
        cache.set('dest_page_count', page_count)
        print('Page count obtained and cached: {}'.format(cache.get('dest_page_count')))

        # Set how data will be cached
        page_block = []
        page_block_size = 20

        for page in range(1, page_count + 1):

            # Include page as a request parameters
            p['page'] = page

            # Retry until response status code 200
            attempt = 0
            valid_response = False
            while not valid_response:
                response = requests.request("GET", url, headers=h, params=p)
                print(response)
                if response.status_code == 200:
                    valid_response = True
                attempt += 1
                if attempt == 30:
                    continue

            d = response.json()

            updated_dest = []
            for item in d['destinations']:
                u = {'iata': item['iata'], 'city': item['city']}
                updated_dest.append(u)

            page_block += updated_dest

            if page % page_block_size == 0 or page == page_count:

                # Set up cache key names
                key = 'dest_{}'.format(page)
                timestamp_key = key + '_timestamp'
                start_key = key + '_start'
                end_key = key + '_end'

                s = page_block[0]['iata']
                if not s:
                    s = 'ZZZ'

                e = page_block[-1]['iata']
                if not e:
                    e = 'ZZZ'

                # Set cache values
                cache.set(key, page_block)
                cache.set(timestamp_key, timezone.now())
                cache.set(start_key, )
                cache.set(end_key, page_block[-1]['iata'])

                cache.set('dest_pages_cached', page)

                msg = 'Page {}: {} destinations were cached.'
                print(msg.format(page, len(page_block)))
                print('Block start: {}. End:{}.'.format(cache.get(start_key), cache.get(end_key)))

                page_block = []

        return 'Destinations successfully cached'
    else:
        print(response)
