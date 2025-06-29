"""
Tests for the Book API with JWT authentication.
"""
import os
import tempfile

from PIL import Image
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Book
from django.contrib.auth import get_user_model

from book.serializers import BookSerializer


BOOKS_URL = reverse('book:book-list')
MY_BOOKS_URL = reverse('book:book-mine')
TOKEN_URL = reverse('user:login')
CREATE_USER_URL = reverse('user:create')


def detail_url(book_id):
    """Return book detail URL"""
    return reverse('book:book-detail', args=[book_id])


def image_upload_url(book_id):
    """Return URL for book image upload."""
    return reverse('book:book-upload-image', args=[book_id])


def create_user(**params):
    """Helper to create user"""
    return get_user_model().objects.create_user(**params)


def create_book(user, **params):
    """Helper to create book"""
    defaults = {
        'title': 'Sample Book',
        'author': 'Sample Author',
        'description': 'Sample description.',
        'condition': 'good',
        'is_available': True,
    }
    defaults.update(params)

    return Book.objects.create(owner=user, **defaults)


class PublicBookApiTests(TestCase):
    """Test unauthenticated book API access"""

    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        """Test retrieving list of available books"""
        user = create_user(
            email='user@example.com',
            password='testpass',
            first_name='Test User',
            last_name='User',
        )
        create_book(user, title='Book 1')
        create_book(user, title='Book 2')

        res = self.client.get(BOOKS_URL)

        books = Book.objects.filter(is_available=True).order_by('-id')
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        """Test retrieving a book detail"""
        user = create_user(
            email='user@example.com',
            password='testpass',
            first_name='Test User',
            last_name='User',
        )
        book = create_book(user)

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_unauthorized(self):
        """Test that authentication is required to create a book"""
        payload = {
            'title': 'Unauthorized Book',
            'author': 'Author',
            'description': 'Desc',
            'condition': 'new',
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
            first_name='First Name',
            last_name='Last Name',
        )
        self.client = APIClient()
        self.token = self.get_token(self.user.email, 'testpass123')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )

    def get_token(self, email, password):
        """Helper to get JWT token"""
        res = self.client.post(
            TOKEN_URL, {'email': email, 'password': password})
        return res.data['access']

    def test_create_book(self):
        """Test creating a book"""
        payload = {
            'title': 'Clean Code',
            'author': 'Robert Martin',
            'description': 'A handbook of agile software craftsmanship.',
            'condition': 'good'
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data['id'])
        for k in payload.keys():
            self.assertEqual(getattr(book, k), payload[k])
        self.assertEqual(book.owner, self.user)

    def test_retrieve_my_books(self):
        """Test retrieving books for authenticated user"""
        create_book(user=self.user, title='Book owned by me')
        other_user = create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other User',
            last_name='Other Last Name',
        )
        create_book(user=other_user, title='Book owned by other')

        res = self.client.get(MY_BOOKS_URL)

        books = Book.objects.filter(owner=self.user)
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_book(self):
        """Test updating a book with patch"""
        book = create_book(user=self.user)

        payload = {'title': 'New Title'}
        url = detail_url(book.id)
        res = self.client.patch(url, payload)

        book.refresh_from_db()
        self.assertEqual(book.title, payload['title'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_full_update_book(self):
        """Test full update with put"""
        book = create_book(user=self.user)

        payload = {
            'title': 'Updated Book',
            'author': 'New Author',
            'description': 'New description',
            'condition': 'new',
            'is_available': False
        }
        url = detail_url(book.id)
        res = self.client.put(url, payload)

        book.refresh_from_db()
        for k in payload.keys():
            self.assertEqual(getattr(book, k), payload[k])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_book(self):
        """Test deleting a book"""
        book = create_book(user=self.user)

        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_delete_book_other_users_error(self):
        """Test trying to delete another user's book returns error"""
        new_user = create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other User',
            last_name='Other Last Name',
        )
        book = create_book(user=new_user)

        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=book.id).exists())


class BookImageUploadTests(TestCase):
    """Test uploading an image to a book."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(self.user)
        self.book = create_book(user=self.user)

    def tearDown(self):
        """Clean up any uploaded files after test."""
        if self.book.image:
            self.book.image.delete()

    def test_upload_image_to_book(self):
        """Test uploading an image to book."""
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {
                'image': image_file
            }
            res = self.client.post(url, payload, format='multipart')

        self.book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.book.image.path))

    def test_upload_invalid_image(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.book.id)
        payload = {'image': 'notanimage'}

        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
