from django.urls import path
from .views import ArticleView, ArticleListView, ArticleDetailsView, LatestArticleView

urlpatterns = [
    path('publish/', ArticleView.as_view(), name='publish_article'),
    path('featured/', ArticleListView.as_view(), name='featured_articles'),
    path('read/', ArticleDetailsView.as_view(), name='get_article_by_id'),
    path('latest/', LatestArticleView.as_view(), name='get_latest_articles'),
]