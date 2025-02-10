import django_filters
from rest_framework import status
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Author,Borrower,Book
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from django_filters.rest_framework import DjangoFilterBackend
from .utils import IsAdminOrStaff,IsRegularUser,verify_and_refresh_token,get_tokens_for_user,BookFilter
from .serializers import AuthorSerializer,BookSerializer,UserLoginSerializer,UserSerializer,BorrowerSerializer


class UserLoginView(APIView): 
    permission_classes = [AllowAny]    
    def post(self, request):        
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):           
            user = serializer.validated_data['user']        
            token = get_tokens_for_user(user)       
            user_data = UserSerializer(user).data            
            return Response(
                {'message': 'Login successful', 'user_data': user_data, 'token': token},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    def get_permissions(self):
        if self.action in ['create','update', 'destroy']:            
            permission_classes = [IsAdminOrStaff]
        else:            
            permission_classes = [IsRegularUser]
        return [permission() for permission in permission_classes]

class BookViewSet(viewsets.ModelViewSet):    
    queryset =Book.objects.all().select_related('author').prefetch_related('borrowers')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    #filterset_class = BookFilter # custom Filtering books by author and availability
    filterset_fields = ['author', 'available']
    
    def get_permissions(self):
        if self.action in ['create','update', 'destroy']:  #Admin or Staff can do everything (create, update, delete, retrieve, list) but regular can only view          
            permission_classes = [IsAdminOrStaff]
        else:            
            permission_classes = [IsRegularUser]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        cache_key = 'book_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60*15)
        return Response(serializer.data,status=status.HTTP_200_OK)

class BookSearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        title = self.request.query_params.get('title', None)
        author = self.request.query_params.get('author', None)
        available = self.request.query_params.get('available', None)        
        
        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__name__icontains=author)            
        if available:  
            available = available.lower() == 'yes' if isinstance(available, str) else available
            queryset = queryset.filter(available=available)            
       
        if not queryset.exists():
            return Response({'message': "No books found matching your search criteria."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'message': "Here is the details of Book", 'details': serializer.data}, status=status.HTTP_200_OK)
    
class BorrowBookViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all().select_related('user').prefetch_related('books_borrowed')
    serializer_class = BorrowerSerializer
    permission_classes = [IsRegularUser]

    @action(detail=True, methods=['post'], url_path='borrow', url_name='borrow')
    def borrow_book(self, request, pk=None):
        book_id = request.data.get('book_id', None)

        if not book_id:
            return Response({'detail': 'Book ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'detail': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not book.available:
            return Response({'detail': 'This book is not available for borrowing.'}, status=status.HTTP_400_BAD_REQUEST)

        borrower = Borrower.objects.filter(user=request.user).first() 
        if not borrower:
            return Response({'detail': 'No borrower record found for this user.'}, status=status.HTTP_404_NOT_FOUND) 
        
        if borrower.books_borrowed.count() >= 3:
            return Response({'detail': 'You cannot borrow more than 3 books at a time.'}, status=status.HTTP_400_BAD_REQUEST)

        borrower.books_borrowed.add(book)
        borrower.save()

        book.available = False
        book.save()

        serializer = BorrowerSerializer(borrower)
        return Response({
            'detail': 'Book borrowed successfully.',
            'borrower_data': serializer.data
        }, status=status.HTTP_200_OK)

class ReturnBookViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer
    permission_classes = [IsRegularUser] 
    
    @action(detail=True, methods=['post'], url_path='return', url_name='return-book')
    def return_book(self, request, pk=None): 
                
        book_id = request.data.get('book_id', None)        
        if not book_id:
            return Response({'detail': 'Book ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'detail': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        borrower = Borrower.objects.filter(user=request.user).first()
        if not borrower:
            return Response({'detail': 'No borrower record found for this user.'}, status=status.HTTP_404_NOT_FOUND)

        if book not in borrower.books_borrowed.all():
            return Response({'detail': 'You have not borrowed this book.'}, status=status.HTTP_400_BAD_REQUEST)
        
        borrower.books_borrowed.remove(book)
        book.available = True
        book.save()
        return Response({'detail': 'Book returned successfully.'}, status=status.HTTP_200_OK)
    
    
    