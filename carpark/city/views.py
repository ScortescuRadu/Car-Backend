from django.shortcuts import render
from .serializers import CitySerializer
from .models import City
from rest_framework.generics import ListAPIView

# Create your views here.

class CityListView(ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
