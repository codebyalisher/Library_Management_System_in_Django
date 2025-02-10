from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Author, Book, Borrower

class BaseTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.staff_user = User.objects.create_user(
            username='staff', email='staff@example.com', password='staffpass', is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular', email='regular@example.com', password='regularpass'
        )

        # Create authors and books
        self.author = Author.objects.create(name='Test Author', bio='Test Bio')
        self.book1 = Book.objects.create(
            title='Book 1', isbn='1234567890123', author=self.author, published_date='2023-01-01', available=True
        )
        self.book2 = Book.objects.create(
            title='Book 2', isbn='1234567890124', author=self.author, published_date='2023-01-02', available=True
        )
        self.book3 = Book.objects.create(
            title='Book 3', isbn='1234567890125', author=self.author, published_date='2023-01-03', available=True
        )
        self.book4 = Book.objects.create(
            title='Book 4', isbn='1234567890126', author=self.author, published_date='2023-01-04', available=True
        )

        # Create a borrower for the regular user
        self.borrower = Borrower.objects.create(user=self.regular_user)

class BorrowingLimitTests(BaseTestCase):
    def test_borrow_more_than_3_books(self):
        self.client.force_authenticate(user=self.regular_user)

        # Borrow 3 books
        for book in [self.book1, self.book2, self.book3]:
            response = self.client.post(
                reverse('borrower-borrow', kwargs={'pk': self.borrower.pk}),
                {'book_id': book.id},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Attempt to borrow a 4th book
        response = self.client.post(
            reverse('borrower-borrow', kwargs={'pk': self.borrower.pk}),
            {'book_id': self.book4.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'You cannot borrow more than 3 books at a time.')

class PermissionTests(BaseTestCase):
    def test_admin_can_create_author(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse('author-list'),
            {'name': 'New Author', 'bio': 'New Bio'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_can_create_author(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(
            reverse('author-list'),
            {'name': 'New Author', 'bio': 'New Bio'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_regular_user_cannot_create_author(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            reverse('author-list'),
            {'name': 'New Author', 'bio': 'New Bio'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_book(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            reverse('book-detail', kwargs={'pk': self.book1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_delete_book(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(
            reverse('book-detail', kwargs={'pk': self.book1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
class BorrowReturnTests(BaseTestCase):
    def test_borrow_book(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            reverse('borrower-borrow', kwargs={'pk': self.borrower.pk}),
            {'book_id': self.book1.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Book borrowed successfully.')

        # Check if the book is marked as unavailable
        book = Book.objects.get(id=self.book1.id)
        self.assertFalse(book.available)

    def test_return_book(self):
        self.client.force_authenticate(user=self.regular_user)

        # Borrow a book first
        self.client.post(
            reverse('borrower-borrow', kwargs={'pk': self.borrower.pk}),
            {'book_id': self.book1.id},
            format='json'
        )

        # Return the book
        response = self.client.post(
            reverse('borrower-return', kwargs={'pk': self.borrower.pk}),
            {'book_id': self.book1.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Book returned successfully.')

        # Check if the book is marked as available
        book = Book.objects.get(id=self.book1.id)
        self.assertTrue(book.available)       
