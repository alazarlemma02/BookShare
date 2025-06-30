"""
Tests for the Rental API with JWT authentication.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Rental, Book
from django.contrib.auth import get_user_model
from rental.serializers import RentalSerializer

from datetime import date, timedelta


RENTAL_URL = reverse('rental:rental-list')
MY_RENTALS_URL = reverse('rental:rental-mine')
TOKEN_URL = reverse('user:login')
CREATE_USER_URL = reverse('user:create')


def detail_url(rental_id):
    """Return rental detail URL"""
    return reverse('rental:rental-detail', args=[rental_id])


def create_user(**params):
    """Helper to create a user"""
    return get_user_model().objects.create_user(**params)


def create_book(user, **params):
    """Helper to create a book"""
    defaults = {
        'title': 'Sample Book',
        'author': 'Sample Author',
        'description': 'Sample description',
        'condition': 'good',
        'is_available': True,
    }
    defaults.update(params)
    return Book.objects.create(owner=user, **defaults)


def create_rental(user, book, **params):
    """Helper to create a rental"""
    defaults = {
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=7),
        'status': 'ongoing'
    }
    defaults.update(params)
    return Rental.objects.create(renter=user, book=book, **defaults)


class PublicRentalApiTests(TestCase):
    """Test unauthenticated rental API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RENTAL_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRentalApiTests(TestCase):
    """Test authenticated rental API access"""

    def setUp(self):
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client = APIClient()
        self.token = self.get_token(self.user.email, 'testpass123')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )

    def get_token(self, email, password):
        """Helper to get JWT token"""
        res = self.client.post(
            TOKEN_URL, {'email': email, 'password': password}
        )
        return res.data['access']

    def test_retrieve_rentals(self):
        """Test retrieving rentals"""
        book = create_book(user=self.user)
        create_rental(user=self.user, book=book)

        res = self.client.get(RENTAL_URL)

        rentals = Rental.objects.filter(renter=self.user).order_by('-id')
        serializer = RentalSerializer(rentals, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_my_rentals(self):
        """Test retrieving authenticated user's rentals"""
        book1 = create_book(user=self.user, title="Book One")
        book2 = create_book(user=self.user, title="Book Two")

        create_rental(user=self.user, book=book1)
        create_rental(user=self.user, book=book2)

        res = self.client.get(MY_RENTALS_URL)

        rentals = Rental.objects.filter(
            renter=self.user
        ).order_by('-request_date')
        serializer = RentalSerializer(rentals, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_rental(self):
        """Test creating a rental"""
        owner = create_user(
            email='owner@example.com',
            password='testpass123'
        )
        book = create_book(user=owner)

        payload = {
            'book': book.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=5)),
        }

        res = self.client.post(RENTAL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        rental = Rental.objects.get(id=res.data['id'])
        self.assertEqual(rental.book, book)
        self.assertEqual(rental.renter, self.user)

    def test_partial_update_rental(self):
        """Test updating a rental with patch"""
        book = create_book(user=self.user)
        rental = create_rental(user=self.user, book=book, status='accepted')

        url = reverse('rental:rental-mark-as-returned', args=[rental.id])
        res = self.client.post(url)

        rental.refresh_from_db()
        self.assertEqual(rental.status, 'returned')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_rental(self):
        """Test deleting a rental"""
        book = create_book(user=self.user)
        rental = create_rental(user=self.user, book=book)

        url = detail_url(rental.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Rental.objects.filter(id=rental.id).exists())
