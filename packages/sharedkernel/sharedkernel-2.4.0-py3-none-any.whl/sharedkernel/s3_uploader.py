
import requests
import boto3
from io import BytesIO
import uuid
import os
from sharedkernel.multipart_upload import MultipartUploadSession

class S3Uploader:
    def __init__(self, endpoint_url, bucket, access_key, secret_key):
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key

        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
    
    @staticmethod
    def __generate_object_name(object_name=None, file_extension=None, folder_name=None):
        if object_name is None:
            object_name = str(uuid.uuid4())

        if file_extension:
            object_name += file_extension

        if folder_name:
            object_name = f"{folder_name}/{object_name}"
        
        return object_name


    def upload_file_object(self, file_obj, object_name=None, file_extension=None, folder_name=None, public_read=True):
        object_name = self.__generate_object_name(object_name, file_extension, folder_name)

        acl = "public-read" if public_read else "private"

        self.s3.upload_fileobj(file_obj, self.bucket, object_name, ExtraArgs={'ACL': acl})

        file_url = f"{self.endpoint_url}/{self.bucket}/{object_name}"

        return file_url

    def generate_presigned_url(self, object_name=None, file_extension=None, folder_name=None, expire_time: int = 3600):
        object_name = self.__generate_object_name(object_name, file_extension, folder_name)

        temp_url = self.s3.generate_presigned_url(
           'get_object',
           Params={
               'Bucket': self.bucket,
               'Key': object_name
           },
           ExpiresIn=expire_time
       )
        
        return temp_url
        
    def upload_file_from_url(self, file_url, object_name=None, folder_name=None):
        """
        Downloads a file from a URL and uploads it to an S3 bucket, returning its URL.

        :param file_url: URL of the file to download
        :param object_name: S3 file name to save as (optional)
        :param folder_name: Optional folder name to save the file in
        :return: URL of the uploaded file if successful, else False
        """
        # Step 1: Download the file from the provided URL
        response = requests.get(file_url)
        response.raise_for_status()  # Check if the request was successful

        # Extract file extension from the URL if available
        file_extension = os.path.splitext(file_url)[1]  # Get extension from URL (e.g., .jpg, .mp3, etc.)
        
        # Use the filename from the URL if no object_name is provided, otherwise use uuid4
        if object_name is None:
            object_name = str(uuid.uuid4())  # Default to UUID if filename can't be extracted

        # Step 2: Upload the file to S3
        file_obj = BytesIO(response.content)
        return self.upload_file_object(file_obj=file_obj, object_name=object_name, file_extension=file_extension, folder_name=folder_name)

    def create_multipart_session(
        self,
        object_name=None,
        file_extension=None,
        folder_name=None,
        public_read=True,
    ):
        object_key = self.__generate_object_name(
            object_name, file_extension, folder_name
        )

        acl = "public-read" if public_read else "private"

        return MultipartUploadSession(
            s3_client=self.s3,
            bucket=self.bucket,
            object_key=object_key,
            acl=acl,
        )


