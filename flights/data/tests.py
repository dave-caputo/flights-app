from django.test import TestCase

from data.models import Enroute


class ListAndEnrouteModelsTest(TestCase):

    def test_default_fields(self):
        flight = Enroute()
        self.assertEqual(flight.ident, '')
        self.assertEqual(flight.aircrafttype, '')
        self.assertEqual(flight.actualdeparturetime, 0)
        self.assertEqual(flight.estimatedarrivaltime, 0)
        self.assertEqual(flight.filed_departuretime, 0)
        self.assertEqual(flight.origin, '')
        self.assertEqual(flight.destination, '')
        self.assertEqual(flight.originName, '')
        self.assertEqual(flight.originCity, '')
        self.assertEqual(flight.destinationName, '')
        self.assertEqual(flight.destinationCity, '')
