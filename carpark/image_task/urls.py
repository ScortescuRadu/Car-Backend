from django.urls import path
from .views import UserImageTasksView, ProcessFrameView, CreateEntranceExitView, ProcessEntranceExitView

urlpatterns = [
    path('by-user/', UserImageTasksView.as_view(), name='user-image-tasks'),
    path('process-frames/', ProcessFrameView.as_view(), name='process-frames'),
    path('create-entrance-exit/', CreateEntranceExitView.as_view(), name='create_entrance_exit'),
    path('process-entrance-exit/', ProcessEntranceExitView.as_view(), name='process_entrance_exit'),
]