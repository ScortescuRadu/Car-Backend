from django.shortcuts import render
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer, ArticlesListSerializer
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import LimitOffsetPagination
import math
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

class CustomPagination(PageNumberPagination):
    page_size = 1 # default page size
    max_page_size = 1000 # default max page size
    page_size_query_param = 'page_size' # if you want to dynamic items per page from request you must have to add it 
      
    def get_paginated_response(self, data):
        # if you want to show page size in resposne just add these 2 lines
        if self.request.query_params.get('page_size'):
            self.page_size = int(self.request.query_params.get('page_size'))
            
        # you can count total page from request by total and page_size
        total_page = math.ceil(self.page.paginator.count / self.page_size)
        
        # here is your response
        return Response({
            'count': self.page.paginator.count,
            'total': total_page,
            'page_size': self.page_size,
            'current': self.page.number,
            'previous': self.get_previous_link(),
            'next': self.get_next_link(),
            'results': data
        })

# GET all Articles
class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.filter(is_featured=True)
    serializer_class = ArticlesListSerializer
    pagination_class = CustomPagination

# GET all Articles
class ArticleDetailsView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(is_featured=True)
    serializer_class = ArticlesListSerializer

    def get(self, request, *args, **kwargs):
        try:
            id = request.query_params['id']
            print(id)
            if id != None:
                article = Article.objects.get(id=id)
                serializer = ArticleSerializer(article)
        except:
            articles = self.get_queryset()
            serializer = ArticleSerializer(articles, many=True)

        return Response(serializer.data)
