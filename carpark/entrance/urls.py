from django.urls import path
from .views import EntranceListCreateView

urlpatterns = [
    path('gate/', EntranceListCreateView.as_view(), name='entrance-list-create'),
]