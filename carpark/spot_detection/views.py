from django.shortcuts import render
import json
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import process_image_task
from .models import BoundingBox
from django.views import View
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.views import generic
from .serializers import BoundingBoxSerializer, ImageProcessSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import viewsets, status

# Create your views here.


class ProcessImageView(generics.CreateAPIView):
    serializer_class = ImageProcessSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Get the uploaded image
            image = request.FILES.get('image')

            if image:
                # Convert the image data to base64
                image_base64 = base64.b64encode(image.read()).decode('utf-8')

                # Call the Celery task for image processing
                result = process_image_task.delay(image_base64)

                # Return the task ID for the client to check the status
                return Response({'task_id': result.id}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'error': 'Missing image'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An unexpected error occurred: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckTaskStatusView(View):
    def get(self, request, task_id):
        result = process_image_task.AsyncResult(task_id)

        if result.successful():
            # Task completed successfully
            return JsonResponse({'status': 'SUCCESS', 'result': result.result})
        elif result.failed():
            # Task failed
            return JsonResponse({'status': 'FAILURE', 'message': result.traceback})
        else:
            # Task still in progress
            return JsonResponse({'status': 'PENDING'})


class StoreBoundingBoxesView(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        task_id = data.get('task_id')
        bounding_boxes_json = data.get('bounding_boxes_json')

        BoundingBox.objects.create(task_id=task_id, bounding_boxes_json=bounding_boxes_json)

        return JsonResponse({'message': 'Bounding boxes stored successfully'})

    def get_object(self):
        return get_object_or_404(BoundingBox, pk=self.kwargs['pk'])