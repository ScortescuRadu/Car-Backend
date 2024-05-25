from django.urls import path
from .views import UserImageTasksView, ProcessFrameView

urlpatterns = [
    path('by-user/', UserImageTasksView.as_view(), name='user-image-tasks'),
    path('process-frames/', ProcessFrameView.as_view(), name='user-image-tasks'),
]