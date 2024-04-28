from django.urls import re_path
from .consumers import TaskStatusConsumer

websocket_urlpatterns = [
    re_path(r'^ws/task_status/(?P<task_id>[0-9a-f-]+)/$', TaskStatusConsumer.as_asgi()),
]