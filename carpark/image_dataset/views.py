from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import ImageDataset, ParkingLot
from .serializers import ImageDatasetSerializer, ImageDatasetRetrieveSerializer
# Create your views here.

class ImageDatasetView(generics.CreateAPIView):
    serializer_class = ImageDatasetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        street_address = serializer.validated_data['street_address']
        bounding_boxes = serializer.validated_data['bounding_boxes']
        image = serializer.validated_data['image']
        original_image_width = serializer.validated_data['original_image_width']
        original_image_height = serializer.validated_data['original_image_height']

        # Get or create the ParkingLot
        parking_lot = get_object_or_404(ParkingLot, street_address=street_address)

        # Create the ImageDataset entry
        image_dataset = ImageDataset.objects.create(
            parking_lot=parking_lot,
            image=image,
            bounding_boxes_json=bounding_boxes,
            original_image_width=original_image_width,
            original_image_height=original_image_height
        )

        return Response({'message': 'Image dataset stored successfully'}, status=status.HTTP_201_CREATED)


class ImageDatasetListView(APIView):
    def post(self, request, *args, **kwargs):
        start = request.data.get('start', 0)
        end = request.data.get('end', 15)
        datasets = ImageDataset.objects.all()[start:end]
        serializer = ImageDatasetRetrieveSerializer(datasets, many=True)
        return Response(serializer.data)