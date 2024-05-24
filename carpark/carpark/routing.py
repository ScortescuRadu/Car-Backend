from django.urls import re_path
from .consumers import (
    TaskStatusConsumer,
    ParkingLotUpdateDataConsumer,
    ParkingSpotUpdateConsumer,
    CameraUpdateConsumer)

websocket_urlpatterns = [
    re_path(r'^ws/task_status/(?P<task_id>[0-9a-f-]+)/$', TaskStatusConsumer.as_asgi()),
    re_path(r'ws/parking_lot_updates/$', ParkingLotUpdateDataConsumer.as_asgi()),
    re_path(r'ws/parking_spot_updates/$', ParkingSpotUpdateConsumer.as_asgi()),
    re_path(r'^ws/camera_updates/$', CameraUpdateConsumer.as_asgi()),
]