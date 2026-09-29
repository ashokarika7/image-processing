import boto3
import os

from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client('s3',
                 region_name=os.getenv('AWS_DEFAULT_REGION'),
                 endpoint_url=f"https://s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com"    
                         )

BUCKET_NAME = os.getenv('BUCKET_NAME')

def generate_presigned_upload_url(object_key: str, content_type: str, expiration: int = 300):
    url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=expiration,
    )

    return url

def download_image(bucket_name, object_key):
    file_name = object_key.split("/")[-1]
    
    s3_client.download_file(
        bucket_name,
        object_key,
        f"/tmp/{file_name}"
    )

    return f"/tmp/{file_name}"

if __name__ == "__main__":
    url = generate_presigned_upload_url(
        "images/test.jpg"
    )

    print(url)