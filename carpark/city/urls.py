from django.urls import path
from .views import CityListView

urlpatterns = [
    # Other URL patterns
    path('cities/', CityListView.as_view(), name='list_of_cities'),
]