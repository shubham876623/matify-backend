import boto3
import uuid
import os

from dotenv import load_dotenv
load_dotenv()
def upload_file_to_s3(image_file):
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
    return public_url