from django.urls import path
from .views import UserParkListCreateView

urlpatterns = [
    path('user-park/', UserParkListCreateView.as_view(), name='user-parks-list-create'),
]