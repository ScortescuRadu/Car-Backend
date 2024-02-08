from django.urls import path
from .views import UserProfilePictureUpload, UserProfilePictureRetrieve

urlpatterns = [
    path('change/', UserProfilePictureUpload.as_view(), name='change_profile_picture'),
    path('display/', UserProfilePictureRetrieve.as_view(), name='display_profile_picture'),
]