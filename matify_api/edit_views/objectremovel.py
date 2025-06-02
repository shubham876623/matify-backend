
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.urls import path
from  matify_api.runpodapisetup.runpodapis import call_runpod_sync
from rest_framework.response import Response
import base64
import requests
from matify_api.services.uploadtos3 import upload_file_to_s3


class ObjectRemoverView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        
        if 'main_image' in request.FILES:
             main_image = upload_file_to_s3(request.FILES['main_image'])
  
        elif 'image_url' in request.POST:
            main_image = request.POST.get('image_url')
            
            
        mask_url = upload_file_to_s3(request.FILES["mask_image"])
        print(main_image)
        main_image_url = main_image
        endpoint_id = "327kodc7ivalpf"
        
       
        input_payload = {
            "input": {
                "image": main_image_url,
                "mask":mask_url,
                 "mask_threshold": 240,
                    "gaussblur_radius": 8,
                    "image_format": "jpeg",
                    "image_quality": 95

               
            }
        }
        print(input_payload ,"ojectremoval")
        result = call_runpod_sync(endpoint_id, input_payload)
        print(result ,"zzz")
        return Response(result['output'][0]['image'])