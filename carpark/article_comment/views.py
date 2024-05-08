from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, permissions
from .models import Comment
from .serializers import CommentSerializer, NewCommentSerializer, CommentLikeDislikeSerializer
from rest_framework.response import Response
from article.models import Article
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_object_or_404

# Create your views here.

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = NewCommentSerializer

    def perform_create(self, serializer, *args, **kwargs):
        user_token = self.request.data.get('access_token')

        user = self.request.user if self.request.user.is_authenticated else None
        if user is None and user_token:
            try:
                user = Token.objects.get(key=user_token).user
            except Token.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        print('aha')
        print(user)
        article_id = self.request.data.get('article_id')
        try:
            article = Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

        parent_comment_id = self.request.data.get('parent_comment')
        parent_comment = None
        if parent_comment_id:
            try:
                parent_comment = Comment.objects.get(pk=parent_comment_id)
            except Comment.DoesNotExist:
                return Response({"error": "Parent comment not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            article_id = int(article_id) if article_id else None
            parent_comment_id = int(parent_comment_id) if parent_comment_id else None
        except ValueError:
            raise ValidationError("Article ID and Parent Comment ID must be integers.")

        serializer.save(user=user, article_id=article_id, parent_comment_id=parent_comment_id)


class CommentListByArticleView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        article_id = self.kwargs['article_id']
        return Comment.objects.filter(article_id=article_id)


class CommentLikeAPIView(APIView):
    def post(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        if 'like' in request.data:
            if request.data['like']:
                comment.likes += 1
            else:
                comment.likes = max(comment.likes - 1, 0)
        comment.save()
        serializer = CommentLikeDislikeSerializer(comment)
        return Response(serializer.data)


class CommentDislikeAPIView(APIView):
    def post(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        if 'dislike' in request.data:
            if request.data['dislike']:
                comment.dislikes += 1
            else:
                comment.dislikes = max(comment.dislikes - 1, 0)
        comment.save()
        serializer = CommentLikeDislikeSerializer(comment)
        return Response(serializer.data)
