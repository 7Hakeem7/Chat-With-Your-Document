import boto3
import os

BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'aiplanet7')

def upload_file_to_s3(file_path, bucket_name=BUCKET_NAME):
    s3_client = boto3.client('s3')
    file_name = os.path.basename(file_path)
    s3_client.upload_file(file_path, bucket_name, file_name)
    print(f"File {file_name} uploaded to {bucket_name}")