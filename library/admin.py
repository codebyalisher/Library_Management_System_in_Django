# librarymanagement/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .models import Author, Book, Borrower

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio')
    search_fields = ('name',)
    
    # Allow only Admin or Staff users to add, change or delete authors
    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'author', 'published_date', 'available','last_borrowed_date')
    list_filter = ('available', 'author')
    search_fields = ('title', 'isbn', 'author__name')

    # Allow only Admin or Staff users to add, change or delete books
    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

class BorrowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_books_borrowed_count')
    
    # Restrict permissions to Admin users only for adding or changing Borrower models
    def has_add_permission(self, request):
        return request.user.is_superuser  # Only admin can add borrowers

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser  # Only admin can change borrowers
    
    def get_books_borrowed_count(self, obj):
        return obj.books_borrowed.count()
    
    get_books_borrowed_count.short_description = 'Books Borrowed'

# Register the models with the customized admin classes
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Borrower, BorrowerAdmin)
