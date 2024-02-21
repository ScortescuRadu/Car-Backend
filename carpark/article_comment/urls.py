from django.urls import path
from .views import CommentCreateView, CommentListByArticleView

urlpatterns = [
    path('comments/', CommentCreateView.as_view(), name='comment-create'),
    path('comments/article/<int:article_id>/', CommentListByArticleView.as_view(), name='comment-list-by-article'),
]