from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, UpdateUserInfoView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register_user'),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('info', UpdateUserInfoView.as_view(), name='update_user_info'),
]