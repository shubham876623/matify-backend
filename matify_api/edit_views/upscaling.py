
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.urls import path
from  matify_api.runpodapisetup.runpodapis import call_runpod_sync
from rest_framework.response import Response
import base64
import requests
import boto3
from matify_api.services.uploadtos3 import upload_file_to_s3
import uuid
import os
class UpscaleImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image_url = request.data.get("image_url")
        image_file = request.FILES.get("image")
        scale = int(request.data.get("scale", 2))

        # Case 1: URL input
        if image_url:
            public_url = image_url

        # Case 2: Local file upload -> upload to S3
        elif image_file:
            try:
                content_type = image_file.content_type or 'image/jpeg'
                file_key = f"uploads/{uuid.uuid4().hex}_{image_file.name}"

                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_S3_REGION_NAME")
                )

                s3.upload_fileobj(
                    image_file,
                    os.getenv("Upscaling_bucket_name"),
                    file_key,
                    ExtraArgs={'ContentType': content_type}
                )

                public_url = (
                    f"https://{os.getenv('Upscaling_bucket_name')}.s3."
                    f"{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/{file_key}"
                )
            except Exception as e:
                return Response({"error": f"Failed to upload image: {str(e)}"}, status=500)
        else:
            return Response({"error": "Either image_url or image file must be provided."}, status=400)

        # Call Replicate
        headers = {
            "Authorization": f"Bearer {os.getenv('REPLICATE_TOKEN')}",
            "Content-Type": "application/json",
            "Prefer": "wait"
        }
        # print(public_url)
        payload = {
            "version": "tencentarc/gfpgan:297a243ce8643961d52f745f9b6c8c1bd96850a51c92be5f43628a0d3e08321a",
            "input": {
                "img": public_url,
                "scale": scale,
                "version": "v1.4"
            }
        }

        # try:
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(response.json()['urls']['get'])
        #again request to get the final output
        response = requests.get(response.json()['urls']['get'],headers = { "Authorization": f"Bearer {os.getenv('REPLICATE_TOKEN')}"})
      
        return Response(response.json()['output'], status=200)