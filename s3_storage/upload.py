# s3_storage/upload.py
import boto3
import json
import os
from io import BytesIO
import requests

class S3Uploader:
    def __init__(self, bucket_name, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def upload_json(self, data, s3_path):
        """
        Upload a Python dict (data) as a JSON file to S3.
        """
        json_str = json.dumps(data, indent=2)
        self.s3_client.put_object(
            Body=json_str,
            Bucket=self.bucket_name,
            Key=s3_path,
            ContentType='application/json'
        )
        print(f"JSON data uploaded to s3://{self.bucket_name}/{s3_path}")

    def upload_image_from_url(self, image_url, s3_path):
        """
        Download an image from a URL and upload it directly to S3.
        """
        response = requests.get(image_url)
        if response.status_code == 200:
            file_obj = BytesIO(response.content)
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, s3_path, ExtraArgs={'ContentType': content_type})
            print(f"Image uploaded to s3://{self.bucket_name}/{s3_path}")
        else:
            print(f"Failed to download image from {image_url}")
