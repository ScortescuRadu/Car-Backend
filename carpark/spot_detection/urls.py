from django.urls import path
from .views import ProcessImageView, CheckTaskStatusView, StoreBoundingBoxesView

urlpatterns = [
    path('process_image/', ProcessImageView.as_view(), name='process_image'),
    path('store_bounding_boxes/', StoreBoundingBoxesView.as_view(), name='store_bounding_boxes'),
    path('check_task_status/<str:task_id>/', CheckTaskStatusView.as_view(), name='check_task_status'),
]