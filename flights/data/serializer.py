from rest_framework import serializers

from data.models import Enroute


class EnrouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enroute
        fields = ('ident', 'aircrafttype', 'actualdeparturetime',
            'estimatedarrivaltime', 'filed_departuretime','origin',
            'destination', 'originName', 'originCity',
            'destinationName', 'destinationCity')
        # exclude = ('id',)
