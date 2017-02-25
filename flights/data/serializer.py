from rest_framework import serializers

from data.models import Enroute


class EnrouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enroute
