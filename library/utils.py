import os
import jwt
import django_filters
from.models import Author,Book
from datetime import datetime
from dotenv import load_dotenv
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):        
        return request.user.is_staff or request.user.is_superuser

class IsRegularUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):        
        return request.user.is_authenticated

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token    
    return {
        'refresh': str(refresh),
        'access': str(access_token),
    }

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token is expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')

def verify_and_refresh_token(request):
    token = request.headers.get('Authorization').split(' ')[1]  
    try:        
        verify_token(token)
    except AuthenticationFailed as e:
        if 'expired' in str(e).lower():            
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                raise AuthenticationFailed('Refresh token is required')
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return {'access': new_access_token}
        else:
            raise e
    return {'status': 'valid'}

class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Search by title')
    author = django_filters.ModelChoiceFilter(queryset=Author.objects.all(), label='Filter by author')
    available = django_filters.BooleanFilter(label='Filter by availability')

    class Meta:
        model = Book
        fields = ['title', 'author', 'available']