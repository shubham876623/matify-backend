from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.urls import path
from  matify_api.runpodapisetup.runpodapis import call_runpod_sync
from rest_framework.response import Response
import base64
import requests
from matify_api.services.uploadtos3 import upload_file_to_s3
class BackgroundReplacementView(APIView):
    # permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        prompt = request.data.get("prompt", "")
        if "image" in request.FILES:
            image_data = request.FILES["image"]
            public_url = upload_file_to_s3(image_data)
        elif "image_url" in request.data:
            image_url = request.data["image_url"]
            public_url = image_url
        else:
            return Response({"error": "No image or image URL provided"}, status=400)
        print(public_url)
        print(prompt)
        endpoint_id = "burkgsza0ugbt0"
        input_payload = {
            "input": {
                "image": public_url,
                "prompt":prompt,
                
             
            }
        }
        result = call_runpod_sync(endpoint_id, input_payload)
        print(result)
        return Response(result['output'][0]['image'])

