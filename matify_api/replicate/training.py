import uuid
import os
import boto3
from io import BytesIO
from zipfile import ZipFile

from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response

from dotenv import load_dotenv
import requests

from matify_api.models import TrainedModel

load_dotenv()

# --------------------------
# Helper: Upload file to S3
# --------------------------
def upload_file_to_s3(file_obj, filename, content_type):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_S3_REGION_NAME")
        )

        file_key = f"{uuid.uuid4().hex}_{filename}"

        s3.upload_fileobj(
            file_obj,
            os.getenv('AWS_STORAGE_BUCKET_NAME'),
            file_key,
            ExtraArgs={'ContentType': content_type}
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


# --------------------------
# View: Model Training
# --------------------------
class ReplicateModelTrainingView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        zip_file_upload = request.FILES.get("zip_file")
        trigger_word = request.data.get("trigger_word")

        if not zip_file_upload or not trigger_word:
            return Response({"error": "Missing zip file or trigger word"}, status=400)

        # Read ZIP file into memory
        zip_bytes = zip_file_upload.read()
        zip_file_for_s3 = BytesIO(zip_bytes)
        zip_file_for_extract = BytesIO(zip_bytes)

        # Upload ZIP to S3
        zip_file_url = upload_file_to_s3(
            file_obj=zip_file_for_s3,
            filename=zip_file_upload.name,
            content_type=zip_file_upload.content_type
        )

        if not zip_file_url:
            return Response({"error": "Failed to upload ZIP to S3"}, status=500)

        # Extract first image from ZIP and upload it
        first_image_url = None
        try:
            with ZipFile(zip_file_for_extract, 'r') as zip_ref:
                for name in zip_ref.namelist():
                    if name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                        with zip_ref.open(name) as image_file:
                            image_bytes = BytesIO(image_file.read())
                            first_image_url = upload_file_to_s3(
                                image_bytes,
                                filename=name,
                                content_type='image/jpeg'  # Optional: determine dynamically
                            )
                        break
        except Exception as e:
            print("Error extracting image from ZIP:", str(e))

        if not first_image_url:
            return Response({"error": "No image found in ZIP"}, status=400)

        # Prepare Replicate API call
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
                "input_images": zip_file_url,
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
            print("Replicate Response:", res.status_code, res.text)

            if res.ok:
                response_json = res.json()
                training_id = response_json.get("id")
                version_id = response_json.get("version")
                status = response_json.get("status", "starting")
                created_at = response_json.get("created_at")

                # Save training info to DB
                TrainedModel.objects.create(
                    user=request.user,
                    training_id=training_id,
                    version_id=version_id,
                    status=status,
                    trigger_word=trigger_word,
                    created_at=created_at,
                    image_url=first_image_url
                )

                return Response(response_json)

            else:
                return Response({
                    "error": "Replicate API failed",
                    "status": res.status_code,
                    "details": res.text
                }, status=500)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
