"""
Views for Rental API.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Rental
from rental import serializers
from rest_framework.exceptions import ValidationError


class RentalViewSet(viewsets.ModelViewSet):
    """Manage rentals in the database."""
    serializer_class = serializers.RentalSerializer
    queryset = Rental.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return rentals for books that I own (incoming requests)."""
        return self.queryset.filter(
            book__owner=self.request.user
        ).order_by('-request_date')

    def perform_create(self, serializer):
        """Create a new rental request."""
        book = serializer.validated_data['book']
        if book.owner == self.request.user:
            raise ValidationError(
                "You cannot rent your own book."
            )
        if not book.is_available:
            raise ValidationError(
                "This book is currently not available."
            )
        serializer.save(renter=self.request.user)

    @action(methods=['GET'], detail=False, url_path='mine')
    def mine(self, request):
        """Retrieve rentals I have requested (as renter)."""
        rentals = self.queryset.filter(
            renter=request.user
        ).order_by('-request_date')
        serializer = self.get_serializer(rentals, many=True)
        return Response(serializer.data)

    @action(
        methods=['POST'],
        detail=True,
        url_path='accept',
        serializer_class=None
    )
    def accept(self, request, pk=None):
        """Accept a rental request (by owner only)."""
        rental = self.get_object()
        if rental.book.owner != request.user:
            return Response({'error': 'Not authorized.'},
                            status=status.HTTP_403_FORBIDDEN)

        if rental.status != 'pending':
            return Response({'error': 'Rental is not pending.'},
                            status=status.HTTP_400_BAD_REQUEST)

        rental.status = 'accepted'
        rental.book.is_available = False
        rental.book.save()
        rental.save()
        return Response({'status': 'Rental accepted.'})

    @action(
        methods=['POST'],
        detail=True,
        url_path='decline',
        serializer_class=None
    )
    def decline(self, request, pk=None):
        """Decline a rental request."""
        rental = self.get_object()
        if rental.book.owner != request.user:
            return Response({'error': 'Not authorized.'},
                            status=status.HTTP_403_FORBIDDEN)

        if rental.status != 'pending':
            return Response({'error': 'Rental is not pending.'},
                            status=status.HTTP_400_BAD_REQUEST)

        rental.status = 'declined'
        rental.save()
        return Response({'status': 'Rental declined.'})

    @action(
        methods=['POST'],
        detail=True,
        url_path='return',
        serializer_class=None
    )
    def mark_as_returned(self, request, pk=None):
        """Mark a rental as returned."""
        rental = self.get_object()
        if rental.renter != request.user and rental.book.owner != request.user:
            return Response({'error': 'Not authorized.'},
                            status=status.HTTP_403_FORBIDDEN)

        if rental.status != 'accepted':
            return Response({'error': 'Rental is not active.'},
                            status=status.HTTP_400_BAD_REQUEST)

        rental.status = 'returned'
        rental.book.is_available = True
        rental.book.save()
        rental.save()
        return Response(
            {'status': 'Rental marked as returned.'},
            status=status.HTTP_200_OK
        )
