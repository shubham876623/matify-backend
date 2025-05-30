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
from matify_api.models import TrainedModel ,Gallery

from matify_api.serializers import TrainedModelSerializer ,GallerySerializer
from django.utils.dateparse import parse_datetime

from matify_api.models import TrainedModel


class ReplicatePredictionView(APIView):
    def post(self, request):
        replicate_token = os.getenv("REPLICATE_TOKEN")
        if not replicate_token:
            return Response({"error": "Replicate token not set"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Extract data
        version = request.data.get("version").split(":")[1]
        # print(version)
        # print(input_data)
        input_data = request.data.get("input")
        if not version or not input_data:
            return Response(
                {"error": "Both 'version' and 'input' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = {
            "Authorization": f"Token {replicate_token}",
            "Content-Type": "application/json",
            "Prefer": "wait"
        }

        payload = {
            "version": version,
            "input":input_data
        }

        try:
            r = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
            r.raise_for_status()
            return Response(r.json(), status=r.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)