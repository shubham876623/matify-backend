from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from rest_framework.parsers import MultiPartParser ,JSONParser ,  FormParser
from dotenv import load_dotenv
import requests
from django.core.files.storage import default_storage
import replicate
import os
import boto3
import uuid
import requests
from django.conf import settings
import base64
from rest_framework.decorators import api_view
import json
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from matify_api.models import TrainedModel , Gallery
from matify_api.serializers import TrainedModelSerializer ,GallerySerializer
from django.utils.dateparse import parse_datetime


class GalleryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        images = Gallery.objects.filter(user=request.user).order_by('-created_at')
        serializer = GallerySerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        image_url = request.data.get("image_url")
        if not image_url:
            return Response({"error": "Missing image URL"}, status=400)

        gallery_image = Gallery.objects.create(user=request.user, image_url=image_url)
        return Response(GallerySerializer(gallery_image).data, status=201)
    
    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response({"error": "ID required to delete"}, status=400)

        try:
            item = Gallery.objects.get(pk=item_id, user=request.user)
            item.delete()
            return Response({"message": "🗑️ Deleted"}, status=204)
        except Gallery.DoesNotExist:
            return Response({"error": "Not found"}, status=404)