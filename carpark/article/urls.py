from django.urls import path
from .views import ArticleView, ArticleListView

urlpatterns = [
    path('publish/', ArticleView.as_view(), name='publish_article'),
    path('featured/', ArticleListView.as_view(), name='feartured_articles'),
]