"""
Serializers for Rental API.
"""
from rest_framework import serializers
from core.models import Rental


class RentalSerializer(serializers.ModelSerializer):
    """Serializer for Rental objects."""

    class Meta:
        model = Rental
        fields = [
            'id', 'renter', 'book', 'status', 'request_date',
            'start_date', 'end_date', 'message'
        ]
        read_only_fields = ['id', 'renter', 'status', 'request_date']
