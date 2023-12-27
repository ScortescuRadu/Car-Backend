from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'cover', 'title', 'description', 'timestamp',
                'cover_section_1', 'subtitle_1', 'description_1',
                'cover_section_2', 'subtitle_2', 'description_2',
                'latitude', 'longitude',
                'is_featured'
                ]

# For retrieving all articles
class ArticlesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'cover', 'title', 'description', 'timestamp',
                'is_featured'
                ]
