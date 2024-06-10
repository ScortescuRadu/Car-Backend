from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import ImageDataset, ParkingLot
from .serializers import ImageDatasetSerializer, ImageDatasetRetrieveSerializer
import os
import json
import zipfile
from io import BytesIO
from random import shuffle
from django.http import HttpResponse
from django.views import View
from sklearn.model_selection import train_test_split

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


class DownloadDatasetView(View):
    def get(self, request, *args, **kwargs):
        # Fetch all ImageDataset objects
        all_images = list(ImageDataset.objects.all())
        # Shuffle the dataset to ensure random distribution
        shuffle(all_images)

        # Split the dataset into train, valid, and test sets
        train_images, test_images = train_test_split(all_images, test_size=0.2, random_state=42)
        train_images, valid_images = train_test_split(train_images, test_size=0.25, random_state=42)  # 0.25 x 0.8 = 0.2

        # Create a BytesIO object to hold the ZIP file
        zip_buffer = BytesIO()

        # Create a ZIP file
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            data = []

            # Create directories inside the ZIP file
            zip_file.writestr('xpark-dataset/README.roboflow.txt', 'This is a dataset exported from the Django app.')
            zip_file.writestr('xpark-dataset/data.yaml', 'paths:\n  train: train/images\n  val: valid/images\n  test: test/images\n\nnames:\n  0: empty\n')

            for split in ['train', 'valid', 'test']:
                zip_file.writestr(f'xpark-dataset/{split}/images/', '')
                zip_file.writestr(f'xpark-dataset/{split}/labels/', '')

            def add_images_and_labels(images, split):
                for item in images:
                    image_path = item.image.path
                    image_name = os.path.basename(image_path)

                    # Add the image to the ZIP file in the appropriate directory
                    zip_file.write(image_path, f'xpark-dataset/{split}/images/{image_name}')

                    # Prepare annotation data in YOLO format
                    yolo_annotations = []
                    for bbox in item.bounding_boxes_json:
                        box_points = bbox['box']

                        if isinstance(box_points[0], dict):  # If points are dictionaries with 'x' and 'y' keys
                            x_center = (box_points[0]['x'] + box_points[2]['x']) / 2 / item.original_image_width
                            y_center = (box_points[0]['y'] + box_points[2]['y']) / 2 / item.original_image_height
                            width = (box_points[2]['x'] - box_points[0]['x']) / item.original_image_width
                            height = (box_points[2]['y'] - box_points[0]['y']) / item.original_image_height
                        else:  # If points are already normalized floats
                            x_center = (box_points[0] + box_points[2]) / 2
                            y_center = (box_points[1] + box_points[3]) / 2
                            width = (box_points[2] - box_points[0])
                            height = (box_points[3] - box_points[1])

                        class_id = 0  # Assuming a single class "A" for simplicity
                        yolo_annotations.append(f"{class_id} {x_center} {y_center} {width} {height}")

                    # Save annotations to a text file within the ZIP
                    annotation_path = f'xpark-dataset/{split}/labels/{os.path.splitext(image_name)[0]}.txt'
                    zip_file.writestr(annotation_path, "\n".join(yolo_annotations))

            # Add images and labels to the appropriate splits
            add_images_and_labels(train_images, 'train')
            add_images_and_labels(valid_images, 'valid')
            add_images_and_labels(test_images, 'test')

        # Set the pointer of the BytesIO object to the beginning
        zip_buffer.seek(0)

        # Create an HTTP response with the ZIP file
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=dataset.zip'

        return response