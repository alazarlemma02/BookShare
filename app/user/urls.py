"""
URL mapping for the user API.
"""
from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('login/', views.CreateTokenView.as_view(), name='login'),
    path(
        'token/refresh/',
        views.CustomTokenRefreshView.as_view(),
        name='token_refresh',
    ),
    path('me/', views.ManageUserView.as_view(), name='me'),
]
