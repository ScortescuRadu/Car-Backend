from django.urls import path
from .views import (ArticleView,
    ArticleListView,
    ArticleDetailsView,
    LatestArticleView,
    LatestGreenArticleView,
    TopReadArticlesLastWeekView,
    ExcludedArticlesView,
    SearchArticlesView)

urlpatterns = [
    path('publish/', ArticleView.as_view(), name='publish_article'),
    path('featured/', ArticleListView.as_view(), name='featured_articles'),
    path('read/', ArticleDetailsView.as_view(), name='get_article_by_id'),
    path('latest/', LatestArticleView.as_view(), name='get_latest_articles'),
    path('latest-green/', LatestGreenArticleView.as_view(), name='latest-green-article'),
    path('top-read-last-week/', TopReadArticlesLastWeekView.as_view(), name='top-read-articles-last-week'),
    path('excluded-articles/', ExcludedArticlesView.as_view(), name='excluded-articles'),
    path('search/', SearchArticlesView.as_view(), name='search-articles'),
]