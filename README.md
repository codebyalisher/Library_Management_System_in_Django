# Library Management System

A Django-based Library Management System API to manage books, authors, and borrowers with role-based permissions.

## Project Overview

This project is a simplified Library Management System API built with Django. The API allows users to perform CRUD operations on Books, Authors, and Borrowers. User authentication is implemented to restrict certain operations based on user roles (admin, staff, regular user).

## Features

- User authentication and authorization
- Role-based permissions (admin, staff, regular user)
- CRUD operations for authors and books
- Borrowing and returning books
- Search functionality for books
- Admin dashboard

## Requirements

### Models

- **Author**:
  - `name`
  - `bio`
- **Book**:
  - `title`
  - `isbn`
  - `author` (ForeignKey to Author)
  - `published_date`
  - `available` (indicates if the book is available for borrowing)
- **Borrower**:
  - `user` (ForeignKey to Django User model)
  - `books_borrowed` (ManyToManyField to Book with a limit of 3 books at any given time)

### Views and API Endpoints

- **Author Management**:
  - Create, read, update, and delete authors.
  - Only staff and admin users can create, update, or delete authors.
- **Book Management**:
  - CRUD operations for books.
  - Books can only be created or updated by staff or admin users.
  - Anyone (authenticated or anonymous) can view books.
- **Borrowing Books**:
  - Regular users can "borrow" a book if it's available.
  - Borrowers cannot borrow more than 3 books at once.
  - Borrowing a book changes the available status of the book to False.
  - A "return book" option allows users to return borrowed books and make them available again.

### Authentication and Permissions

- Use Django's authentication system.
- Implement role-based permissions:
  - **Admin**: Full access to all actions.
  - **Staff**: Can manage authors and books but cannot manage users or assign roles.
  - **Regular User**: Can borrow/return books but cannot create or update authors or books.
- Protect API endpoints using Django REST Framework’s (DRF) authentication and permission classes.

### Data Validation

- Ensure ISBN uniqueness and a valid ISBN format on book creation.
- Validate that a borrower does not exceed the borrowing limit.

### Unit Testing

- Write unit tests to validate the functionality of each API endpoint:
  - Test that a user cannot borrow more than 3 books.
  - Test permissions for creating, updating, and deleting authors and books.
  - Test the borrowing and returning book process.
- Use `django.test.TestCase` or `pytest` to structure tests for views and models.

### Bonus Tasks

- **Caching**: Implement caching for frequently accessed book list API to reduce database load.
- **Search and Filtering**: Add a search endpoint for books by title and filtering options by author and availability.
- **Signals**: Use Django signals to automatically update a `last_borrowed_date` on the Book model whenever a book is borrowed.
- **Error Handling**: Implement proper error handling for situations like attempting to borrow an unavailable book or attempting to borrow more than the allowed limit.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/LibraryManagementSystem.git
    cd LibraryManagementSystem
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Apply migrations:

    ```bash
    python manage.py migrate
    ```

5. Create a superuser:

    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

7. Open your browser and go to `http://127.0.0.1:8000/` to access the application.

## API Endpoints

- `http://127.0.0.1:8000/api/login/` for login
- `http://127.0.0.1:8000/api/crud/authors/` for CRUD operations on authors
- `http://127.0.0.1:8000/api/crud/books/` for CRUD operations on books
- `http://127.0.0.1:8000/api/crud/borrow/` for borrowing books
- `http://127.0.0.1:8000/api/crud/return/` for returning books
- `http://127.0.0.1:8000/api/crud/search/` for searching books

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature/your-feature-name`).
6. Open a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Bootstrap](https://getbootstrap.com/)