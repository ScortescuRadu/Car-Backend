from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import OperatingHours
from .serializers import OperatingHoursSerializer

# Create your views here.

class OperatingHoursListCreateView(generics.ListCreateAPIView):
    queryset = OperatingHours.objects.all()
    serializer_class = OperatingHoursSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if an entry with the same data already exists
        day = serializer.validated_data['day']
        opening_time = serializer.validated_data['opening_time']
        closing_time = serializer.validated_data['closing_time']

        existing_entry = OperatingHours.objects.filter(
            day=day,
            opening_time=opening_time,
            closing_time=closing_time
        ).first()

        if existing_entry:
            error_message = "Operating hours with the same data already exist."
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        # If no duplicate, proceed with the creation
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status.HTTP_201_CREATED, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()