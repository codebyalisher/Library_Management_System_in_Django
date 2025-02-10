from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Borrower

# Signal to update last_borrowed_date when a book is borrowed
@receiver(post_save, sender=Borrower)
def update_last_borrowed_date(sender, instance, **kwargs):
    for book in instance.books_borrowed.all():
        book.last_borrowed_date = timezone.now()
        book.save()
        