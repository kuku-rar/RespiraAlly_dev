# services/web-app/app/core/minio_service.py

import boto3
from botocore.exceptions import ClientError
from flask import current_app
import uuid
import logging
from urllib.parse import urlparse, urlunparse

class MinioService:
    def __init__(self, endpoint_url, access_key, secret_key, secure=False, public_url=None):
        self.endpoint_url = endpoint_url
        self.public_url = public_url if public_url else endpoint_url
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=boto3.session.Config(signature_version='s3v4'),
            region_name='us-east-1'  # Required for s3v4
        )

    def generate_presigned_upload_url(self, bucket_name, object_name=None, expiration=3600):
        if object_name is None:
            object_name = f"audio-{uuid.uuid4().hex}.wav"

        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                logging.error(f"Error checking bucket: {e}")
                raise

        try:
            response = self.s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration,
                HttpMethod='PUT'
            )
            return {'url': response, 'object_name': object_name}
        except ClientError as e:
            logging.error(f"Error generating presigned URL: {e}")
            return None

    def upload_file_content(self, bucket_name, object_name, data, length, content_type='application/octet-stream', metadata=None):
        """
        Uploads file-like object or bytes to MinIO with optional metadata.
        """
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                logging.error(f"Error checking bucket: {e}")
                raise

        try:
            put_params = {
                'Bucket': bucket_name,
                'Key': object_name,
                'Body': data,
                'ContentLength': length,
                'ContentType': content_type
            }
            if metadata:
                put_params['Metadata'] = metadata

            self.s3_client.put_object(**put_params)
            logging.info(f"Successfully uploaded {object_name} to bucket {bucket_name}.")
            return True
        except ClientError as e:
            logging.error(f"Error uploading file to MinIO: {e}")
            return False

    def generate_presigned_get_url(self, bucket_name, object_name, expiration=3600):
        """
        Generate a presigned URL to share an S3 object, ensuring it uses the public-facing URL.
        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid.
        :return: Presigned URL as string. If error, returns None.
        """
        try:
            # Generate the URL using the internal endpoint
            internal_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )

            # Replace the internal endpoint with the public one for external access
            internal_parts = urlparse(internal_url)
            public_parts = urlparse(self.public_url)

            # Reconstruct the URL with the public scheme, netloc, and keep the rest from the generated URL
            final_url_parts = internal_parts._replace(
                scheme=public_parts.scheme,
                netloc=public_parts.netloc
            )

            final_url = urlunparse(final_url_parts)
            return final_url

        except ClientError as e:
            logging.error(f"Error generating presigned GET URL: {e}")
            return None

    def get_object_size(self, bucket_name, object_name):
        """
        Get the size of an object in a bucket.
        :param bucket_name: string
        :param object_name: string
        :return: Size of the object in bytes. If error, returns None.
        """
        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=object_name)
            return response.get('ContentLength')
        except ClientError as e:
            logging.error(f"Error getting object size for {object_name}: {e}")
            return None

# --- Service Singleton ---
_minio_service = None

def get_minio_service():
    """
    Factory function to get the singleton instance of MinioService.
    It now prioritizes a specific BASE_URL for generating external links.
    """
    global _minio_service
    if _minio_service is None:
        # Fall back to BASE_URL for backward compatibility, but it's less ideal.
        public_url = current_app.config.get('BASE_URL')

        if not public_url:
            logging.warning("BASE_URL is not set. Presigned URLs may be incorrect for external access.")
            # If no public URL is set, it will default to the internal endpoint_url inside MinioService

        # Determine scheme for internal connection based on MINIO_SECURE flag
        scheme = 'https' if current_app.config.get('MINIO_SECURE') else 'http'
        endpoint_url = f"{scheme}://{current_app.config['MINIO_ENDPOINT']}"
        _minio_service = MinioService(
            endpoint_url=endpoint_url,
            access_key=current_app.config['MINIO_ACCESS_KEY'],
            secret_key=current_app.config['MINIO_SECRET_KEY'],
            secure=current_app.config.get('MINIO_SECURE', False),
            public_url=public_url
        )
    return _minio_service
