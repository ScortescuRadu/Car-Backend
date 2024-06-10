from django.urls import path
from .views import ImageDatasetView, ImageDatasetListView, DownloadDatasetView

urlpatterns = [
    path('create/', ImageDatasetView.as_view(), name='image-dataset'),
    path('images/', ImageDatasetListView.as_view(), name='image-dataset-list'),
    path('download-dataset/', DownloadDatasetView.as_view(), name='download-dataset'),
]