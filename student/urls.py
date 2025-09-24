from django.urls import path
from .views import signup, login, logout

urlpatterns = [
    path('signup/', signup, name='student-signup'),
    path('login/', login, name='student-login'),
    path('logout/', logout, name='student-logout'),
]