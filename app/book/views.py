"""
Views for the book API.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Book
from book import serializers


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow read-only for everyone; write only for owners."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class BookViewSet(viewsets.ModelViewSet):
    """Manage books in the database."""
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in [
            'create', 'update', 'partial_update', 'destroy',
            'mine', 'upload_image'
        ]:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        """Filter books based on action."""
        if self.action == 'mine':
            return self.queryset.filter(
                owner=self.request.user).order_by('-id')
        if self.action == 'list':
            return self.queryset.order_by('-id')
        return self.queryset

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'upload_image':
            return serializers.BookImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Attach the authenticated user as the book owner."""
        serializer.save(owner=self.request.user)

    @action(methods=['GET'], detail=False, url_path='mine')
    def mine(self, request):
        """Retrieve books for the authenticated user."""
        books = self.get_queryset()
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a book."""
        book = self.get_object()
        serializer = serializers.BookImageSerializer(
            book,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
