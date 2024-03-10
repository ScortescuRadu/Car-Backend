from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import process_image_task

# Create your views here.

def SpotInitView(request):
    image_path = 'path/to/your/image.jpg'
    result = process_image.delay(image_path)
    return HttpResponse(f'Task ID: {result.id}')