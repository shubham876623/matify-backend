
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.urls import path
from  matify_api.runpodapisetup.runpodapis import call_runpod_sync
from rest_framework.response import Response
import base64
from rest_framework import status

import requests
from matify_api.services.uploadtos3 import upload_file_to_s3


class ColorCorrectionView(APIView):
    def post(self, request):
        if "main_image" in  request.FILES:
            image_url = upload_file_to_s3(request.FILES.get("main_image"))
        else:    
             image_url = request.POST.get("image_url")

        payload = {
            "input": {
                "image": image_url,
                
            }
        }

        endpoint_id = "o9ky7zq0ib4bsb"
        result = call_runpod_sync(endpoint_id, payload)
        
        return Response(result['output'][0]['image'])
            
