"""
Tests for Models
"""
from django.test import TestCase
from core import models
from django.contrib.auth import get_user_model


def create_user(email="user@example.com", password="testpass123"):
    """Helper function to create a user."""
    return get_user_model().objects.create_user(email, password)


class UserModelTests(TestCase):
    """
    Test cases for models
    """

    def test_create_user_with_email_successful(self):
        """
        Test creating a new user with an email is successful
        """
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test the email for a new user is normalized
        """
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["test2@example.COM", "test2@example.com"],
            ["test3@example.com", "test3@example.com"],
            ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "test123")
            self.assertEqual(user.email, expected)

    def test_new_user_invalid_email(self):
        """
        Test creating user with no email raises error
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_new_superuser(self):
        """
        Test creating a new superuser
        """
        user = get_user_model().objects.create_superuser(
            "test@example.com", "test123")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class BookModelTests(TestCase):
    """Test the book model."""

    def test_create_book_successful(self):
        user = create_user()
        book = models.Book.objects.create(
            owner=user,
            title='Clean Code',
            author='Robert C. Martin',
            description='A Handbook of Agile Software Craftsmanship',
            condition='Good'
        )

        self.assertEqual(str(book), book.title)
        self.assertTrue(book.is_available)

    def test_create_book_with_blank_description(self):
        user = create_user()
        book = models.Book.objects.create(
            owner=user,
            title='Refactoring',
            author='Martin Fowler',
            description='',
            condition='Fair'
        )

        self.assertEqual(book.description, '')
        self.assertTrue(book.is_available)
