from django.urls import path
from .views import UserProfileCreateView, UserProfileByUserView, UserProfileDeleteView

urlpatterns = [
    path('create/', UserProfileCreateView.as_view(), name='create-user-profile'),
    path('info/', UserProfileByUserView.as_view(), name='display-user-profile'),
    path('delete/<int:user_id>/', UserProfileDeleteView.as_view(), name='delete-user-profile'),
]