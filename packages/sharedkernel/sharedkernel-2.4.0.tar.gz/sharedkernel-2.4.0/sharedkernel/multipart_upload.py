class MultipartUploadSession:
    MIN_PART_SIZE = 5 * 1024 * 1024  # 5MB

    def __init__(self, s3_client, bucket, object_key, acl="private"):
        self.s3 = s3_client
        self.bucket = bucket
        self.key = object_key
        self.acl = acl

        self.upload_id = None
        self.parts = []
        self.part_number = 1
        self.buffer = bytearray()

        self._start()

    def _start(self):
        resp = self.s3.create_multipart_upload(
            Bucket=self.bucket,
            Key=self.key,
            ACL=self.acl,
        )
        self.upload_id = resp["UploadId"]

    def upload_chunk(self, chunk: bytes):
        """
        Receives small chunks (KB) and buffers them
        """
        self.buffer.extend(chunk)

        if len(self.buffer) >= self.MIN_PART_SIZE:
            self._upload_part(bytes(self.buffer))
            self.buffer.clear()

    def _upload_part(self, data: bytes):
        resp = self.s3.upload_part(
            Bucket=self.bucket,
            Key=self.key,
            UploadId=self.upload_id,
            PartNumber=self.part_number,
            Body=data,
        )

        self.parts.append({
            "ETag": resp["ETag"],
            "PartNumber": self.part_number
        })
        self.part_number += 1

    def complete(self):
        # upload remaining buffer (can be < 5MB)
        if self.buffer:
            self._upload_part(bytes(self.buffer))
            self.buffer.clear()

        self.s3.complete_multipart_upload(
            Bucket=self.bucket,
            Key=self.key,
            UploadId=self.upload_id,
            MultipartUpload={"Parts": self.parts},
        )

    def abort(self):
        if self.upload_id:
            self.s3.abort_multipart_upload(
                Bucket=self.bucket,
                Key=self.key,
                UploadId=self.upload_id,
            )
