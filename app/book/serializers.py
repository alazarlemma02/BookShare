"""
Serializers for the book API.
"""
from rest_framework import serializers
from core.models import Book
from user.serializers import UserPublicSerializer


class BookSerializer(serializers.ModelSerializer):
    """Serializer for book objects."""
    owner = UserPublicSerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'owner',
            'condition', 'is_available', 'created_at', 'image'
        ]
        read_only_fields = ['id', 'created_at', 'owner']


class BookImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to books."""

    class Meta:
        model = Book
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {
            'image': {'required': True}
        }
