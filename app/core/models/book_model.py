from django.db import models
from django.conf import settings
import uuid
import os


def book_image_file_path(instance, filename):
    """Generate file path for new book image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'book', filename)


class Book(models.Model):
    """Book object representing a user's book for lending."""
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='books'
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='good',
    )
    is_available = models.BooleanField(default=True)
    image = models.ImageField(
        null=True,
        upload_to=book_image_file_path,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
