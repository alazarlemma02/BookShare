"""
Views for the user API.
"""
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)
from user.serializers import (
    UserSerializer,
    CustomAuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(TokenObtainPairView):
    """Create a new JWT token for user"""
    serializer_class = CustomAuthTokenSerializer


class CustomTokenRefreshView(BaseTokenRefreshView):
    # Override methods or add custom logic as needed
    pass


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user
