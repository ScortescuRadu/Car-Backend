from django.shortcuts import render
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer, ArticlesListSerializer
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
# Create your views here.

class ArticleView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *arg, **kwargs):
        cover = request.data['cover']
        title = request.data['title']
        description = request.data['description']
        
        cover_section_1 = request.data['cover_section_1']
        subtitle_1 = request.data['subtitle_1']
        description_1 = request.data['description_1']

        cover_section_2 = request.data['cover_section_2']
        subtitle_2 = request.data['subtitle_2']
        description_2 = request.data['description_2']
        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        latitude = float(latitude) if latitude else None
        longitude = float(request.data['longitude']) if longitude else None

        is_featured = bool(request.data.get('is_featured', False))

        Article.objects.create(cover=cover, title=title, description=description,
                            cover_section_1=cover_section_1, subtitle_1=subtitle_1, description_1=description_1,
                            cover_section_2=cover_section_2, subtitle_2=subtitle_2, description_2=description_2,
                            latitude=latitude, longitude=longitude, is_featured=is_featured
                            )

        return Response("Article created successfully", status=status.HTTP_200_OK)

# GET all Articles
class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticlesListSerializer

    search_fields = ['title']
    ordering_fields = ['timestamp']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        # Retrieve only featured articles
        queryset = Article.objects.filter(is_featured=True)
        return queryset