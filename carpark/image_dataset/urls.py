from django.urls import path
from .views import ImageDatasetView

urlpatterns = [
    path('create/', ImageDatasetView.as_view(), name='image-dataset'),
]