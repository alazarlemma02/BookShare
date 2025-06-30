"""
URL Mapping for Rental API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rental import views

router = DefaultRouter()
router.register('rentals', views.RentalViewSet)

app_name = 'rental'

urlpatterns = [
    path('', include(router.urls)),
]
