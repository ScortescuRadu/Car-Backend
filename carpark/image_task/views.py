from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from .models import ImageTask, ParkingLot
from .serializers import ImageTaskUserInputSerializer, ImageTaskUserOutputSerializer
from user_park.models import UserPark
# Create your views here.

class UserImageTasksView(generics.GenericAPIView):
    serializer_class = ImageTaskUserInputSerializer
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
         # Get the user from the token
        user_token = self.request.query_params.get('token')
        user = self.request.user if self.request.user.is_authenticated else None
        if user is None and user_token:
            try:
                user = Token.objects.get(key=user_token).user
            except Token.DoesNotExist:
                return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get the parking lots associated with the user
        user_parks = UserPark.objects.filter(user=user)
        parking_lots = [user_park.parking_lot for user_park in user_parks]

        # Get the ImageTasks associated with these parking lots
        image_tasks = ImageTask.objects.filter(parking_lot__in=parking_lots)

        response_serializer = ImageTaskUserOutputSerializer(image_tasks, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)