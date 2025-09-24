from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    allbooks, addbook, deletebook, issuerequest, myissues, issue_book, return_book,
    requestedissues, myfines, allfines, deletefine, payfine, pay_status, filter_books_by_category,
    CustomTokenObtainPairView, CustomTokenRefreshView, RegistrationView, ProfileView, user_login,
    CategoryViewSet, AuthorViewSet, BookViewSet, IssueViewSet, FineViewSet, dashboard
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'fines', FineViewSet, basename='fine')

urlpatterns = [
    path('',allbooks,name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('books/<str:category>/',filter_books_by_category, name='filter_books'),
    path('addbook/',addbook),
    path('deletebook/<int:bookID>/',deletebook),
    path('request-book-issue/<int:bookID>/',issuerequest),
    path('my-issues/',myissues),
    path('my-fines/',myfines),
    path('payfines/<int:fineID>/',payfine),
    path('paystatus/<int:fineID>/',pay_status),
    path('all-issues/',requestedissues),
    path('all-fines/',allfines),
    path('issuebook/<int:issueID>/',issue_book),
    path('returnbook/<int:issueID>/',return_book),
    path('delete-fine/<int:fineID>/',deletefine),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegistrationView.as_view(), name='register'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/login/', user_login, name='user-login'),
    path('api/', include(router.urls)),
]