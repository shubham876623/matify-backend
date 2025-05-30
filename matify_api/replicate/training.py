       
import uuid
from rest_framework.permissions import IsAuthenticated
import boto3
import os
from rest_framework.parsers import MultiPartParser ,JSONParser ,  FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
import requests

from matify_api.models import TrainedModel
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("REPLICATE_TOKEN")
segmind_api_key = os.getenv('SEGMIND_API_KEY')


print(os.getenv('AWS_S3_REGION_NAME'))

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
                "steps": 2500,
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
        
        



