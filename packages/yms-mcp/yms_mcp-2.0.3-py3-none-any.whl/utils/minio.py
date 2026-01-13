from minio import Minio
from minio.error import S3Error
import uuid
import io

# 加载env文件中的变量
from dotenv import load_dotenv
load_dotenv()

from os import getenv
MINIO_ENDPOINT = getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = getenv("MINIO_BUCKET")
MINIO_PROXY_ENDPOINT = getenv("MINIO_PROXY_ENDPOINT")

print("MINIO_ENDPOINT:", MINIO_ENDPOINT)
print("MINIO_ACCESS_KEY:", MINIO_ACCESS_KEY)
print("MINIO_SECRET_KEY:", MINIO_SECRET_KEY)
print("MINIO_BUCKET:", MINIO_BUCKET)
print("MINIO_PROXY_ENDPOINT:", MINIO_PROXY_ENDPOINT)

def upload_to_minio(image_data: bytes) -> str:
    # Initialize client
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False  # Set to False if using HTTP
    )
    
    # Create bucket if not exists
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
    
    # Generate unique object name
    object_name = f"{uuid.uuid4()}.jpg"
    
    # Upload the image
    client.put_object(
        MINIO_BUCKET,
        object_name,
        io.BytesIO(image_data),
        length=len(image_data),
        content_type='image/jpeg'
    )

    
    # return f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"
    return f"{MINIO_PROXY_ENDPOINT}/{MINIO_BUCKET}/{object_name}"