from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.urls import path
from  matify_api.runpodapisetup.runpodapis import call_runpod_sync
from rest_framework.response import Response
import base64
import requests
from matify_api.services.uploadtos3 import upload_file_to_s3
import random
import json


class AddAccessoriesView(APIView):
    def post(self, request):
        endpoint_id = "wdyxzpu7zkk35p"
       
        if "main_image" in request.FILES:
            main_image_url = upload_file_to_s3(request.FILES["main_image"])
        elif "image_url" in request.data :
            main_image_url = request.data["image_url"]
            
        
        object_image_url = request.FILES["reference_image"]
        mask_image_url = upload_file_to_s3(request.FILES["mask_image"])
        prompt = "photo of person wearing accessory"
        seed = request.data.get("seed", random.randint(0, 999999))
        

        object_image_url = upload_file_to_s3(object_image_url)
        
       
      
        input_payload =  {
        "input": {
            "subject_image": object_image_url,
            "model_image": main_image_url,
            "mask_image": mask_image_url,
            "prompt":"exaclty where the mask is pointing"
           
        }
        }
        print(input_payload)
        result = call_runpod_sync(endpoint_id, input_payload)
        # result  = json.dumps(result, indent=4)
        print(result)
        return Response(result['output'][0]['image'])