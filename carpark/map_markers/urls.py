from django.urls import path
from .views import MarkerView, MarkerListView

urlpatterns = [
    path('markers/', MarkerListView.as_view(), name='get_markers'),
    path('mark/', MarkerView.as_view(), name='post_marker'),
]
