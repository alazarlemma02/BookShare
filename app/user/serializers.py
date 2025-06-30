"""
Serializers for the user API
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users objects"""

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'password',
            'first_name',
            'last_name',
            'profile_picture',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'profile_picture': {'required': False},
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and returning it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class CustomAuthTokenSerializer(TokenObtainPairSerializer):
    """Custom JWT Serializer that returns extra user info"""

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add extra responses here if needed
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        return data
