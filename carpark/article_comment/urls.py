from django.urls import path
from .views import CommentCreateView, CommentListByArticleView, CommentLikeAPIView, CommentDislikeAPIView

urlpatterns = [
    path('publish/', CommentCreateView.as_view(), name='comment-create'),
    path('article/<int:article_id>/', CommentListByArticleView.as_view(), name='comment-list-by-article'),
    path('<int:pk>/like/', CommentLikeAPIView.as_view(), name='comment-like'),
    path('<int:pk>/dislike/', CommentDislikeAPIView.as_view(), name='comment-dislike'),
]