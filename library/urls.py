from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, BookViewSet, UserLoginView, BorrowBookViewSet, ReturnBookViewSet,BookSearchViewSet

router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet,basename='books')
router.register(r'search', BookSearchViewSet, basename='search')
router.register(r'borrow', BorrowBookViewSet, basename='borrow')
router.register(r'return', ReturnBookViewSet, basename='return')  

urlpatterns = [
    path('crud/', include(router.urls)),
    path('login/',UserLoginView.as_view(), name='UserLoginView'),
]
