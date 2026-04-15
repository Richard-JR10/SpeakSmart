# app/services/r2_storage.py
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from app.config import settings

# Initialize R2 client once at module load
_s3_client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4"),
    region_name="auto",
)


def upload_audio(file_bytes: bytes, object_key: str, content_type: str = "audio/wav") -> str:
    """
    Uploads audio bytes to R2.
    Returns the public URL of the uploaded file.

    object_key examples:
      student-audio/{student_uid}/{attempt_id}.wav
      reference-audio/{module_id}/{phrase_id}.wav
    """
    try:
        _s3_client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=object_key,
            Body=file_bytes,
            ContentType=content_type,
        )
        return f"{settings.R2_PUBLIC_URL}/{object_key}"
    except ClientError as e:
        raise RuntimeError(f"R2 upload failed for {object_key}: {e}")


def download_audio(object_key: str) -> bytes:
    """
    Downloads audio bytes from R2 into memory.
    Used by the scoring pipeline to fetch reference audio.
    """
    try:
        response = _s3_client.get_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=object_key,
        )
        return response["Body"].read()
    except ClientError as e:
        raise RuntimeError(f"R2 download failed for {object_key}: {e}")


def delete_audio(object_key: str) -> None:
    """
    Deletes an audio file from R2.
    Used for cleanup or when a student deletes an attempt.
    """
    try:
        _s3_client.delete_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=object_key,
        )
    except ClientError as e:
        raise RuntimeError(f"R2 delete failed for {object_key}: {e}")


def get_object_key_from_url(url: str) -> str:
    """
    Extracts the R2 object key from a full public URL.
    
    Example:
      Input:  https://your-bucket.r2.dev/reference-audio/module_greetings/ph_001.wav
      Output: reference-audio/module_greetings/ph_001.wav
    """
    base = settings.R2_PUBLIC_URL.rstrip("/")
    return url.replace(f"{base}/", "")