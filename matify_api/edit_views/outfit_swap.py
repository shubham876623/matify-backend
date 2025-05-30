
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.urls import path
from  matify_api.runpodapisetup.runpodapis import call_runpod_sync
from rest_framework.response import Response
import base64
import requests
from matify_api.services.uploadtos3 import upload_file_to_s3


class OutfitSwapView(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    def post(self, request):
        endpoint_id = "jfnu2fz5sqtu87"
        

        # Get person image
        if "person_image" in request.FILES:
            person_image_data = upload_file_to_s3(request.FILES["person_image"])
        elif "person_url" in request.data:
            person_image_data = request.data["person_url"]
           

        # Get outfit image
        if "outfit_image" not in request.FILES:
            return Response({"error": "reference_image is required."}, status=400)

        outfit_image_data = upload_file_to_s3(request.FILES["outfit_image"])
        
        
        input_payload = {
        "input": {
            "outfit_image": outfit_image_data,
            "model_image": person_image_data,   #person image
           
        }
        }
        print(input_payload ,"outfitswap")
        result = call_runpod_sync(endpoint_id, input_payload)
       
        return Response(result['output'][0]['image'])
