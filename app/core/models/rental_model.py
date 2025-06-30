"""
Rental Database model for the core app.
"""
from django.db import models
from django.conf import settings
from core.models import Book


class Rental(models.Model):
    """Rental transaction between users."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]

    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rentals'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='rentals'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    request_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return f'{self.renter} → {self.book} ({self.status})'
