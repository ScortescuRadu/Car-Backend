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
from rest_framework.decorators import api_view

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


class CommentListByArticleView(APIView):
    serializer_class = CommentSerializer

    def post(self, request, *args, **kwargs):
        article_id = self.kwargs['article_id']
        user_token = self.request.data.get('access_token')
        user = self.request.user if self.request.user.is_authenticated else None
        if user is None and user_token:
            try:
                user = Token.objects.get(key=user_token).user
            except Token.DoesNotExist:
                user = None
                print('User not found')

        comments = Comment.objects.filter(article_id=article_id)
        context = {'request': request, 'user': user}
        serializer = CommentSerializer(comments, many=True, context=context)
        
        return Response(serializer.data)

class CommentLikeAPIView(APIView):
    def post(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)

            user_token = self.request.data.get('access_token')
            user = self.request.user if self.request.user.is_authenticated else None
            if user is None and user_token:
                try:
                    user = Token.objects.get(key=user_token).user
                except Token.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check current like status
            if user in comment.liked_users.all():
                # User is removing their like
                comment.liked_users.remove(user)
                comment.likes -= 1
            else:
                # User is adding a like
                comment.liked_users.add(user)
                comment.likes += 1
                # Remove dislike if it exists
                if user in comment.disliked_users.all():
                    comment.disliked_users.remove(user)
                    comment.dislikes -= 1

            comment.save()
            serializer = CommentLikeDislikeSerializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

class CommentDislikeAPIView(APIView):
    def post(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)

            user_token = self.request.data.get('access_token')
            user = self.request.user if self.request.user.is_authenticated else None
            if user is None and user_token:
                try:
                    user = Token.objects.get(key=user_token).user
                except Token.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check current dislike status
            if user in comment.disliked_users.all():
                # User is removing their dislike
                comment.disliked_users.remove(user)
                comment.dislikes -= 1
            else:
                # User is adding a dislike
                comment.disliked_users.add(user)
                comment.dislikes += 1
                # Remove like if it exists
                if user in comment.liked_users.all():
                    comment.liked_users.remove(user)
                    comment.likes -= 1

            comment.save()
            serializer = CommentLikeDislikeSerializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
