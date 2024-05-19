from django.shortcuts import render
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer, ArticlesListSerializer, MainArticlesListSerializer
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import LimitOffsetPagination
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
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

        topic = request.data.get('topic')

        is_featured = bool(request.data.get('is_featured', False))

        Article.objects.create(cover=cover, title=title, description=description,
                            cover_section_1=cover_section_1, subtitle_1=subtitle_1, description_1=description_1,
                            cover_section_2=cover_section_2, subtitle_2=subtitle_2, description_2=description_2,
                            latitude=latitude, longitude=longitude, is_featured=is_featured
                            )

        return Response("Article created successfully", status=status.HTTP_200_OK)

class CustomPagination(PageNumberPagination):
    page_size = 6 # default page size
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

# GET Article details
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

# GET most recent articles
class LatestArticleView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(is_featured=True).order_by('-timestamp')[:5]
    serializer_class = MainArticlesListSerializer

    def get(self, request, *args, **kwargs):
        articles = self.get_queryset()
        serializer = MainArticlesListSerializer(articles, many=True)

        return Response(serializer.data)

# GET most recent green article
class LatestGreenArticleView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(topic='green', is_featured=True).order_by('-timestamp')
    serializer_class = ArticleSerializer

    def get(self, request, *args, **kwargs):
        article = self.get_queryset().first()  # Get the latest green article
        if article:
            serializer = self.serializer_class(article)
            return Response(serializer.data)
        return Response({"detail": "No green articles found."}, status=404)

# GET most read articles article of the week
class TopReadArticlesLastWeekView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        one_week_ago = timezone.now() - timedelta(days=777)
        return Article.objects.filter(timestamp__gte=one_week_ago, is_featured=True).order_by('-read_count')[:5]

    def get(self, request, *args, **kwargs):
        articles = self.get_queryset()
        serializer = self.serializer_class(articles, many=True)
        return Response(serializer.data)

# GET 20 articles that are not features in other sections on mobile
class ExcludedArticlesView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        one_week_ago = timezone.now() - timedelta(days=7)
        latest_5 = Article.objects.filter(is_featured=True).order_by('-timestamp')[:5].values_list('id', flat=True)
        top_5_read = Article.objects.filter(timestamp__gte=one_week_ago, is_featured=True).order_by('-read_count')[:5].values_list('id', flat=True)
        latest_green = Article.objects.filter(topic='green', is_featured=True).order_by('-timestamp').first()

        exclude_ids = list(latest_5) + list(top_5_read)
        if latest_green:
            exclude_ids.append(latest_green.id)

        return Article.objects.filter(is_featured=True).exclude(id__in=exclude_ids).order_by('-timestamp')[:20]

    def get(self, request, *args, **kwargs):
        articles = self.get_queryset()
        serializer = self.serializer_class(articles, many=True)
        return Response(serializer.data)

# Search article
class SearchArticlesView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', None)
        topics = self.request.query_params.get('topic', '')

        print("Query:", query)
        print("Topics:", topics)

        if query is not None and query.strip():  # Check if query is not None and not empty after stripping spaces
            filters = Q(title__icontains=query) | Q(subtitle_1__icontains=query) | Q(subtitle_2__icontains=query)
            if topics:
                topic_list = [t.strip() for t in topics.split(',')]
                filters &= Q(topic__in=topic_list)
                print("Topic List:", topic_list)
            return Article.objects.filter(filters).order_by('-timestamp')[:10]
        elif topics:  # Check if topics is not empty
            topic_list = [t.strip() for t in topics.split(',')]
            print("Topic List:", topic_list)
            return Article.objects.filter(topic__in=topic_list).order_by('-timestamp')[:10]
        else:
            return Article.objects.none()

    def get(self, request, *args, **kwargs):
        articles = self.get_queryset()
        serializer = self.serializer_class(articles, many=True)
        print("Number of articles found:", len(articles))
        return Response(serializer.data)