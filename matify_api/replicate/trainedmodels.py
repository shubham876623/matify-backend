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


class UserTrainedModelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        #  Step 1: Get all Replicate trainings
        replicate_trainings = {}
        headers = {"Authorization": f"Token {os.getenv('REPLICATE_TOKEN')}"}

        try:
            res = requests.get("https://api.replicate.com/v1/trainings", headers=headers)
            if res.status_code == 200:
                for training in res.json().get("results", []):
                    replicate_trainings[training["id"]] = training
        except Exception as e:
            print("⚠️ Failed to fetch Replicate trainings:", e)

        #  Step 2: Get all user's trainings
        user_models = TrainedModel.objects.filter(user=user)
        # user_models = TrainedModel.objects.all()

        #  Step 3: Match & update statuses
        for model in user_models:
            if model.training_id in replicate_trainings:
                remote = replicate_trainings[model.training_id]
                model.status = remote.get("status", model.status)
                try:
                    model.version_id = remote.get("output").get("version", model.version_id)
                except:
                        pass    
                model.created_at = parse_datetime(remote.get("created_at"))
               
                model.save()

        #  Step 4: Return updated list
        serializer = TrainedModelSerializer(user_models.order_by("-created_at"), many=True)
        return Response(serializer.data)