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
from .matify_api.models import TrainedModel ,Gallery
from .matify_api.serializers import TrainedModelSerializer ,GallerySerializer
from django.utils.dateparse import parse_datetime
load_dotenv()
token = os.getenv("REPLICATE_TOKEN")
segmind_api_key = os.getenv('SEGMIND_API_KEY')


print(os.getenv('AWS_S3_REGION_NAME'))





class UserTrainedModelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # ✅ Step 1: Get all Replicate trainings
        replicate_trainings = {}
        headers = {"Authorization": f"Token {os.getenv('REPLICATE_TOKEN')}"}

        try:
            res = requests.get("https://api.replicate.com/v1/trainings", headers=headers)
            if res.status_code == 200:
                for training in res.json().get("results", []):
                    replicate_trainings[training["id"]] = training
        except Exception as e:
            print("⚠️ Failed to fetch Replicate trainings:", e)

        # ✅ Step 2: Get all user's trainings
        user_models = TrainedModel.objects.filter(user=user)
        # user_models = TrainedModel.objects.all()

        # ✅ Step 3: Match & update statuses
        for model in user_models:
            if model.training_id in replicate_trainings:
                remote = replicate_trainings[model.training_id]
                model.status = remote.get("status", model.status)
                model.version_id = remote.get("output").get("version", model.version_id)
                model.created_at = parse_datetime(remote.get("created_at"))
               
                model.save()

        # ✅ Step 4: Return updated list
        serializer = TrainedModelSerializer(user_models.order_by("-created_at"), many=True)
        return Response(serializer.data)


class ReplicatePredictionView(APIView):
    def post(self, request):
        replicate_token = os.getenv("REPLICATE_TOKEN")
        if not replicate_token:
            return Response({"error": "Replicate token not set"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Extract data
        version = request.data.get("version").split(":")[1]
        input_data = request.data.get("input")
        print(version)
        print(input_data)
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
        
def getzipfile_publicurl(zip_file):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_S3_REGION_NAME")
        )

        file_key = f"{uuid.uuid4().hex}_{zip_file.name}"

        s3.upload_fileobj(
        zip_file,
        os.getenv('AWS_STORAGE_BUCKET_NAME'),
        file_key,
        ExtraArgs={'ContentType': zip_file.content_type} 
    )

        public_url = (
            f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3."
            f"{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/{file_key}"
        )
        return public_url

    except Exception as e:
        print("ERROR uploading to S3:", str(e))
        import traceback
        traceback.print_exc()
        return None


class ReplicateModelTrainingView(APIView):
    parser_classes = [MultiPartParser]
   
    permission_classes = [IsAuthenticated]
    def post(self, request):
        zip_file = request.FILES.get("zip_file")
        trigger_word = request.data.get("trigger_word")

        if not zip_file or not trigger_word:
            return Response({"error": "Missing zip file or trigger word"}, status=400)

        #  Upload to S3
        image_url_s3 = getzipfile_publicurl(zip_file)
        if not image_url_s3:
            return Response({"error": "Failed to upload zip to S3"}, status=500)

        #  Prepare Replicate API call
        headers = {
            "Authorization": f"Token {os.getenv('REPLICATE_TOKEN')}",
            "Content-Type": "application/json"
        }

        payload = {
            "destination": os.getenv("REPLICATE_DESTINATION"),
            "input": {
                "steps": 1000,
                "lora_rank": 16,
                "optimizer": "adamw8bit",
                "batch_size": 1,
                "resolution": "512,768,1024",
                "autocaption": True,
                "input_images": image_url_s3,
                "trigger_word": trigger_word,
                "learning_rate": 0.0004,
                "wandb_project": "flux_train_replicate",
                "wandb_save_interval": 100,
                "caption_dropout_rate": 0.05,
                "cache_latents_to_disk": False,
                "wandb_sample_interval": 100,
                "gradient_checkpointing": False
            }
        }

        replicate_url = (
            f"https://api.replicate.com/v1/models/"
            f"{os.getenv('REPLICATE_MODEL_OWNER')}/"
            f"{os.getenv('REPLICATE_MODEL_NAME')}/versions/"
            f"{os.getenv('REPLICATE_MODEL_VERSION_ID')}/trainings"
        )

        try:
            res = requests.post(replicate_url, headers=headers, json=payload)
            print(" Replicate Response:", res.status_code, res.text)

            if res.ok:
                if res.ok:
                    response_json = res.json()
                    training_id = response_json.get("id")
                    version_id = response_json.get("version")  # often None initially
                    status = response_json.get("status", "starting")
                    created_at = response_json.get('created_at')

                    # ✅ Save training record to database
                    TrainedModel.objects.create(
                        user=request.user,
                        training_id=training_id,
                        version_id=version_id,
                        status=status,
                        trigger_word=trigger_word,
                       
                        created_at = created_at
                    )

                return Response(res.json())
            
            else:
                return Response({
                    "error": "Replicate API failed",
                    "status": res.status_code,
                    "details": res.text
                }, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
        
        
        

class GalleryImageUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response({"error": "No image file found."}, status=400)

        # try:
        content_type = image.content_type or 'image/webp'  # fallback if missing
        file_key = f"gallery/{uuid.uuid4().hex}_{image.name}"

        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_S3_REGION_NAME")
        )

        s3.upload_fileobj(
            image,
            os.getenv("GALLERY_BUCKET_NAME"),
            file_key,
            ExtraArgs={'ContentType': content_type}
        )

        public_url = (
            f"https://{os.getenv('GALLERY_BUCKET_NAME')}.s3."
            f"{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/{file_key}"
        )

        return Response({"url": public_url})

        # except Exception as e:
        #     return Response({"error": str(e)}, status=500)

class GalleryListView(APIView):
    def get(self, request):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_S3_REGION_NAME")
        )

        bucket = os.getenv("GALLERY_BUCKET_NAME")
        prefix = "gallery/"  # Only fetch images in gallery folder

        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
        urls = []
        for obj in response.get("Contents", []):
            key = obj["Key"]
            if key.endswith((".jpg", ".jpeg", ".png", ".webp")):
                url = f"https://{bucket}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/{key}"
                urls.append(url)
         
        return Response({"images": urls})
    
    

#Segmind bg-removal api ..
class BackgroundRemoveSegmindView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request):
        prompt = request.data.get("prompt", "")
        negative_prompt = request.data.get("negative_prompt", "blur, CGI, unreal, animated")
        api_key = segmind_api_key
       
        url = "https://api.segmind.com/v1/ppv6"
       
        # Image from upload or URL
        if "image" in request.FILES:
            image_data = request.FILES["image"].read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
        elif "image_url" in request.data:
            image_url = request.data["image_url"]
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                return Response({"error": "Failed to fetch image from URL"}, status=400)
            image_base64 = base64.b64encode(image_response.content).decode("utf-8")
        else:
            return Response({"error": "No image or image URL provided"}, status=400)

        payload = {
            "image": image_base64,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": 42,
            "steps": 30,
            "guidance_scale": 4.5,
            "x_value": 50,
            "y_value": 50,
            "scale": 0.5,
            "megapixel": 1,
            "aspect_ratio": "8:5 (Cinematic View)",
            "image_format": "png",
            "image_quality": 95,
        }

        headers = {"x-api-key": api_key}
        segmind_response = requests.post(url, json=payload, headers=headers)

        if segmind_response.status_code != 200:
            return Response(
                {"error": "Segmind API failed", "details": segmind_response.text},
                status=500,
            )
        # print(segmind_response.text)
        return Response(segmind_response.json())
    
    


class OutfitSwapSegmindView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request):
        segmind_url = "https://api.segmind.com/v1/segfit-v1.1"
        api_key = segmind_api_key

        # Get person image
        if "person_image" in request.FILES:
            person_image_data = request.FILES["person_image"].read()
        elif "person_url" in request.data:
            image_url = request.data["person_url"]
            try:
                resp = requests.get(image_url)
                resp.raise_for_status()
                person_image_data = resp.content
            except Exception as e:
                return Response({"error": f"Failed to fetch outfit image from URL: {e}"}, status=400)
        else:
            return Response({"error": "No outfit image provided."}, status=400)

        # Get outfit image
        if "outfit_image" not in request.FILES:
            return Response({"error": "reference_image is required."}, status=400)

        outfit_image_data = request.FILES["outfit_image"].read()

        # Convert both to base64
        person_image_b64 = base64.b64encode(person_image_data).decode("utf-8")
        outfit_image_b64 = base64.b64encode(outfit_image_data).decode("utf-8")

        # Build payload
        payload = {
            "outfit_image": outfit_image_b64,
            "model_image": person_image_b64,
            "background_description": "white studio background",
            "aspect_ratio": "2:3",
            "model_type": "Balanced",
            "controlnet_type": "openpose",
            "cn_strength": 0.5,
            "cn_end": 0.6,
            "image_format": "png",
            "image_quality": 95,
            "seed": -1,
            "upscale": False,
            "base64": True
        }

        headers = {"x-api-key": api_key}
        segmind_response = requests.post(segmind_url, json=payload, headers=headers)

        if segmind_response.status_code != 200:
            return Response(
                {"error": "Segmind API failed", "details": segmind_response.text},
                status=500
            )

        result = segmind_response.json()
        return Response({"image": result.get("image")})
    
#objectremove  

def image_file_to_base64(image_path):
    
        image_data = image_path.read()
        return base64.b64encode(image_data).decode('utf-8')

def image_url_to_base64(image_url):
    response = requests.get(image_url)
    image_data = response.content
    return base64.b64encode(image_data).decode('utf-8')

class ObjectRemovalSegmindView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request):
        try:
            main_image = request.FILES["main_image"]
            mask = request.FILES["mask_image"]

            payload = {
                "image": image_file_to_base64(main_image),
                "mask": image_file_to_base64(mask),
                "invert_mask": False,
                "grow_mask": 10,
                "base64": True
            }

            url = "https://api.segmind.com/v1/magic-eraser"
            headers = {"x-api-key": segmind_api_key}

            segmind_response = requests.post(url, json=payload, headers=headers)
            segmind_response.raise_for_status()

            return Response(segmind_response.json())
        
        except KeyError as e:
            return Response({"error": f"Missing file: {e}"}, status=400)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=500)





#upscaling



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
     
     
     
 # Add-Accessories  function        
def image_url_to_base64(image_url):
    response = requests.get(image_url)
    image_data = response.content
    return base64.b64encode(image_data).decode('utf-8')




def image_url_to_base64(image_url):
    response = requests.get(image_url)
    image_data = response.content
    return base64.b64encode(image_data).decode('utf-8')

def image_file_to_base64(image_path):
    
        image_data = image_path.read()
        return base64.b64encode(image_data).decode('utf-8')
    


class AddAccessoriesView(APIView):
    def post(self, request):
        
        print(request.FILES)
        if "main_image" in request.FILES:
            main_image = image_file_to_base64(request.FILES["main_image"])
        elif "image_url" in request.FILES :
            main_image = image_url_to_base64(request.FILES["image_url"])
        
        object_image_url = request.FILES["reference_image"]
        mask_image_url = request.FILES["mask_image"]
        prompt = "photo of person wearing accessory"
        seed = request.data.get("seed", random.randint(0, 999999))
        # print(main_image)

        object_image = image_file_to_base64(object_image_url)
        mask_image = image_file_to_base64(mask_image_url)
        # try:
        payload = {
        "prompt": "apply the mask correctly and retrun the best image",
        "main_image": main_image,
        "object_image":   object_image,
        "mask_image": mask_image,
        "steps": 30,
        "seed":seed,
        "growmask": 5,
        "fashion_strength": 1,
        "subject_strength": 1,
        "horizontal_repeat": 1,
        "vertical_repeat": 1,
        "image_format": "png",
        "image_quality": 95,
        "base64": True
        }

        headers = {"x-api-key": segmind_api_key}
        segmind_response = requests.post(
            "https://api.segmind.com/v1/seg-swap",
            
            json=payload,
            headers=headers,
            timeout=60
        )

        # segmind_response.raise_for_status()
        print(segmind_response.text)
        
        return Response(segmind_response.json())

        # except requests.exceptions.RequestException as e:
        #     return Response({"error": str(e)}, status=500)
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