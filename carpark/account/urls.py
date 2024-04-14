from django.urls import path
from .views import RegisterView, LoginView, UserInfoView, LogoutView, CSRFTokenView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register_user'),
    path('login', LoginView.as_view()),
    path('user', UserInfoView.as_view()),
    path('logout', LogoutView.as_view()),
    path('csrf/', CSRFTokenView.as_view(), name='csrf-token'),
]