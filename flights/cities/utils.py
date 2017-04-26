import re

import requests

from django.db.utils import IntegrityError
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from cities.models import City


class SchipholCityManager:

    def __init__(self):
        self.url = 'https://api.schiphol.nl/public-flights/destinations'
        self.headers = {'resourceversion': 'v1'}
        self.params = {
            'app_id': '7e07d59a',
            'app_key': settings.SCHIPHOL_KEY,
            'sort': '+iata',
            'page': None
        }
        self.max_request_attempts = 30
        self.page_count = self.get_page_count()
        self.last_page_saved = 0
        self.last_item_saved = 0

    def make_request(self, iata=None):
        attempt = 0
        valid_response = False

        url = self.url
        headers = self.headers
        params = self.params

        if iata:
            print('Setting parameters for sending city request for {}'.format(iata))
            url = self.url + '/{}'.format(iata)
            del params['sort']
            del params['page']

        while not valid_response:
            response = requests.request("GET", url, headers=headers,
                                        params=params)
            print('Cities: Request status: {}'.format(response.status_code))
            if response.status_code == 200:
                valid_response = True
            attempt += 1
            if attempt == self.max_request_attempts:
                raise ConnectionError
        print('Match found. Attempts made: {}'.format(attempt))
        return response

    def get_and_save_city(self, iata):

        response = self.make_request(iata=iata)
        data = response.json()
        print(data)
        city = data['city']
        try:
            City.objects.create(iata=iata, city=city)
            print('New city {} saved in the database'.format(city))
        except IntegrityError:
            pass
        return city

    def get_page_count(self):

        self.params['page'] = None

        response = self.make_request()

        # Obtain from headers and cache the number of pages
        link = response.headers['Link']
        page_count = int(re.findall(r'(?<=page\=)\d+', link)[0])

        return page_count

    def get_and_save_page_data(self):

        for page in range(1, self.page_count + 1):

            self.params['page'] = page
            response = self.make_request()
            data = response.json()

            self.save_city_data(data)
            self.last_page_saved = page
            print('Status code:{} page: {}'.format(response.status_code, page))

        return data

    def save_city_data(self, data):

        for i, d in enumerate(data['destinations']):
            try:
                iata = d['iata']
                city = d['city']
            except IntegrityError:
                continue

            if not city or not iata:
                continue
            else:
                try:
                    City.objects.create(city=city, iata=iata)
                    self.last_item_saved = i
                except IntegrityError:
                    continue
