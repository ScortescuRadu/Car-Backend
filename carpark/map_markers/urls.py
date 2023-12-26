from django.urls import path
from .views import MarkerView, MarkerListView, SubscribeToMarkerAPIView

urlpatterns = [
    path('markers/', MarkerListView.as_view(), name='get_markers'),
    path('mark/', MarkerView.as_view(), name='post_marker'),
    path('subscribe/<int:marker_id>/', SubscribeToMarkerAPIView.as_view(), name='subscribe_marker'),
]
