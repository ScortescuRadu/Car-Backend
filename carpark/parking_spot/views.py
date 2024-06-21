from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import ParkingLot, ParkingSpot
from .serializers import ParkingSpotSerializer, ParkingSpotInputSerializer, SpotByAddressInputSerializer
from django.shortcuts import get_object_or_404
from parking_lot.models import ParkingLot
from image_task.models import ImageTask

# Create your views here.

class ParkingSpotCreateView(generics.CreateAPIView):
    serializer_class = ParkingSpotInputSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user_from_token(self, request):
        # Extract user from the authentication token
        user, _ = TokenAuthentication().authenticate(request)
        return user

    def create(self, request, *args, **kwargs):
        user = self.get_user_from_token(request)
        if not user:
            return Response({"detail": "Invalid token or user not found."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        street_address = serializer.validated_data['street_address']

        # Find the parking lot by street address
        parking_lot = get_object_or_404(ParkingLot, street_address=street_address)

        # Create the parking spot
        parking_spot = ParkingSpot(
            parking_lot=parking_lot,
            level=serializer.validated_data['level'],
            sector=serializer.validated_data['sector'],
            number=serializer.validated_data['number'],
            is_occupied=serializer.validated_data['is_occupied']
        )
        parking_spot.save()

        return Response(ParkingSpotSerializer(parking_spot).data, status=status.HTTP_201_CREATED)


class ParkingSpotListView(generics.GenericAPIView):
    serializer_class = SpotByAddressInputSerializer

    def get_queryset(self):
        # This method is required but not used since we handle data fetching in post method.
        return ParkingSpot.objects.none()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        street_address = serializer.validated_data['street_address']

        # Get the ParkingLot by street_address
        parking_lot = get_object_or_404(ParkingLot, street_address=street_address)

        # Get ImageTasks associated with the ParkingLot
        image_tasks = ImageTask.objects.filter(parking_lot=parking_lot, destination_type='spot').prefetch_related('parkingspot_set')

        # Prepare the data to be serialized
        data = []
        for image_task in image_tasks:
            spots = ParkingSpot.objects.filter(image_task=image_task)
            task_data = {
                'camera_address': image_task.camera_address,
                'camera_type': image_task.camera_type,
                'spots': ParkingSpotSerializer(spots, many=True).data
            }
            data.append(task_data)

        return Response(data, status=status.HTTP_200_OK)


class SaveTilesView(APIView):
    def post(self, request):
        selected_address = request.data.get('selectedAddress')
        parking_tiles = request.data.get('parkingTiles')

        if parking_tiles is None:
            return Response({'error': 'No parking tiles provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parking_lot = ParkingLot.objects.get(street_address=selected_address)
            for tile in parking_tiles:
                ParkingSpot.objects.create(
                    parking_lot=parking_lot,
                    level=tile['level'],
                    sector=tile['sector'],
                    number=tile['number'],
                    is_occupied=False
                )
            return Response({'message': 'Parking spots created successfully'}, status=status.HTTP_201_CREATED)
        except ParkingLot.DoesNotExist:
            return Response({'error': 'Parking lot not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)