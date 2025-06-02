import boto3
import uuid
import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def upload_file_to_s3(image_file):
    # Common setup
    region = os.getenv("AWS_S3_REGION_NAME")

    # Case 1: Uploading a file-like object (e.g., from form)
    if hasattr(image_file, 'read'):
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region
        )

        bucket_name = os.getenv("Upscaling_bucket_name")
        content_type = getattr(image_file, 'content_type', 'image/jpeg')
        file_key = f"uploads/{uuid.uuid4().hex}_{image_file.name}"

        s3.upload_fileobj(
            image_file,
            bucket_name,
            file_key,
            ExtraArgs={'ContentType': content_type}
        )

    # Case 2: Uploading an image from URL (e.g., Replicate)
    else:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region
        )

        bucket_name = os.getenv("Genrated_images_BUCKET_NAME")
        response = requests.get(image_file)

        if response.status_code != 200:
            raise Exception(f"Failed to download image: {response.status_code}")

        filename = os.path.basename(urlparse(image_file).path)
        file_key = f"uploads/{uuid.uuid4().hex}_{filename}"

        s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=response.content,
            ContentType='image/webp'
        )

    # Public URL
    public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{file_key}"
    return public_url
