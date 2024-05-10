from rest_framework import serializers
from .models import Comment
from article.models import Article

class CommentSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'article', 'content', 'timestamp', 'parent_comment', 'likes', 'dislikes', 'is_liked', 'is_disliked']

    def get_is_liked(self, obj):
        user = self.context.get('user')
        return obj.liked_users.filter(id=user.id).exists() if user and not user.is_anonymous else False

    def get_is_disliked(self, obj):
        user = self.context.get('user')
        return obj.disliked_users.filter(id=user.id).exists() if user and not user.is_anonymous else False


class NewCommentSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(write_only=True, required=False)  # Declared explicitly, set as write_only for security

    class Meta:
        model = Comment
        fields = ['access_token', 'article_id', 'content', 'parent_comment']

    def create(self, validated_data):
        user = validated_data.get('user')
        article_id = validated_data.get('article_id')
        parent_comment = validated_data.get('parent_comment')
        article = Article.objects.get(pk=article_id) if article_id else None

        return Comment.objects.create(
            user=user,
            article=article,
            content=validated_data['content'],
            parent_comment=parent_comment
        )


class CommentLikeDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'likes', 'dislikes']

    def update(self, instance, validated_data):
        instance.likes = validated_data.get('likes', instance.likes)
        instance.dislikes = validated_data.get('dislikes', instance.dislikes)
        instance.save()
        return instance
