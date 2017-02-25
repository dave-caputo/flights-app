from django.test import TestCase



from data import enroute_test
from data.json_client import FlightClient
from data.models import Enroute
from data.serializer import EnrouteSerializer


class EnrouteModelTest(TestCase):

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

    def test_serializer_saves_objects_to_database(self):
        '''
        Request data is obtained from test file. Use to avoid cost of 
        using live server.
        '''

        data = enroute_test.e['EnrouteResult']['enroute']
        serializer = EnrouteSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
        self.assertEqual(Enroute.objects.count(), 15)
        self.assertEqual(Enroute.objects.filter(ident='HVN55').count(),3)
    
    """
    def test_json_client_imports_file(self):
        '''
        Request data is obtained from file server. Use with caution to
        avoid unnecessary costs.
        '''
        params = {'airport': 'EGLL', 'howMany': 10, 'filter': '', 'offset': 0}
        client = FlightClient('Enroute', params)
        data = client.request.json()
        data = data['EnrouteResult']['enroute']
        serializer = EnrouteSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
        for flight in Enroute.objects.all():
            print(flight.ident + " : " + flight.originCity + " : " + str(flight.estimatedarrivaltime))
        self.assertEqual(Enroute.objects.count(), 10)
    """