from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ImageDataset, ParkingLot
from .serializers import ImageDatasetSerializer
# Create your views here.

class ImageDatasetView(generics.CreateAPIView):
    serializer_class = ImageDatasetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        street_address = serializer.validated_data['street_address']
        bounding_boxes = serializer.validated_data['bounding_boxes']
        image = serializer.validated_data['image']

        # Get or create the ParkingLot
        parking_lot = get_object_or_404(ParkingLot, street_address=street_address)

        # Create the ImageDataset entry
        image_dataset = ImageDataset.objects.create(
            parking_lot=parking_lot,
            image=image,
            bounding_boxes_json=bounding_boxes
        )

        return Response({'message': 'Image dataset stored successfully'}, status=status.HTTP_201_CREATED)