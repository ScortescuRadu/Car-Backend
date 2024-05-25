from django.urls import path
from .views import ImageDatasetView, ImageDatasetListView

urlpatterns = [
    path('create/', ImageDatasetView.as_view(), name='image-dataset'),
    path('images/', ImageDatasetListView.as_view(), name='image-dataset-list'),
]