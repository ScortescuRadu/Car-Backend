from django.urls import path
from .views import RegisterView, LoginView, UserInfoView, LogoutView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register_user'),
    path('login', LoginView.as_view()),
    path('user', UserInfoView.as_view()),
    path('logout', LogoutView.as_view()),
]