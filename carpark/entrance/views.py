from django.shortcuts import render
from rest_framework import generics
from .models import Entrance
from .serializers import EntranceSerializer

# Create your views here.

class EntranceListCreateView(generics.ListCreateAPIView):
    queryset = Entrance.objects.all()
    serializer_class = EntranceSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)