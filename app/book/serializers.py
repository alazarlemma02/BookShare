"""
Serializers for the book API.
"""
from rest_framework import serializers
from core.models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer for book objects."""

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description',
            'condition', 'is_available', 'created_at', 'image'
        ]
        read_only_fields = ['id', 'created_at']


class BookImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to books."""

    class Meta:
        model = Book
        fields = ['id', 'image']
        read_only_fields = ['id']
