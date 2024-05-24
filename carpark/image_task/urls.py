from django.urls import path
from .views import UserImageTasksView

urlpatterns = [
    path('by-user/', UserImageTasksView.as_view(), name='user-image-tasks'),
]