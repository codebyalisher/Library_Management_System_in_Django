# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('regular', 'Regular User'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='regular')

    def is_admin(self):
        return self.role == 'admin'

    def is_staff(self):
        return self.role == 'staff'

    def is_regular_user(self):
        return self.role == 'regular'
    
    groups = models.ManyToManyField(
        Group,
        related_name='library_user_set',  # Custom reverse relationship name
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='library_user_permissions',  # Custom reverse relationship name
        blank=True
    )
    
    class Meta:
        permissions = [
            ("can_manage_authors", "Can manage authors"),
            ("can_manage_books", "Can manage books"),
            ("can_borrow_books", "Can borrow books"),
        ]

# Author model
class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.name

# Book model
class Book(models.Model):
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,related_name="books")
    published_date = models.DateField()
    available = models.BooleanField(default=True)
    last_borrowed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

# Borrower model
class Borrower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="borrower")
    books_borrowed = models.ManyToManyField(Book, blank=True,null=True,related_name="borrowers")

    def __str__(self):
        return self.user.username
