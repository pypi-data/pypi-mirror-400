import os
import shutil
from abc import ABC, abstractmethod
from importlib.metadata import entry_points
from typing import BinaryIO, Dict, Iterator, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from minio import Minio
from minio.error import S3Error
from mypy_boto3_s3 import S3Client

__all__ = [
    "ObjectStorageService",
    "NewClient",
]


class ObjectStorageService(ABC):
    @abstractmethod
    def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None: ...

    @abstractmethod
    def get_object(
        self,
        bucket: str,
        object_name: str,
        chunk_size: int = 8192,
    ) -> Iterator[bytes]: ...

    def get_object_bytes(
        self,
        bucket: str,
        object_name: str,
        chunk_size: int = 8192,
    ) -> bytes:
        return b"".join(self.get_object(bucket, object_name, chunk_size))


class LocalStorageService(ObjectStorageService):
    def __init__(self, root: str):
        self.root = os.path.abspath(root)

    def _path(self, bucket: str, object_name: str) -> str:
        return os.path.join(self.root, bucket, object_name)

    def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type=None,
        metadata=None,
    ) -> None:
        path = self._path(bucket, object_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            shutil.copyfileobj(data, f)

    def get_object(
        self,
        bucket: str,
        object_name: str,
        chunk_size: int = 8192,
    ) -> Iterator[bytes]:
        path = self._path(bucket, object_name)
        with open(path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk


class MinioStorageService(ObjectStorageService):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        region: Optional[str] = None,
        ssl: bool = False,
    ):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            region=region,
            secure=ssl,
        )

    def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        stat = os.fstat(data.fileno())
        self.client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=data,
            length=stat.st_size,
            content_type=content_type,
            metadata=metadata,
        )

    def get_object(
        self,
        bucket: str,
        object_name: str,
        chunk_size: int = 8192,
    ) -> Iterator[bytes]:
        response = None
        try:
            response = self.client.get_object(bucket, object_name)
            for chunk in response.stream(chunk_size):
                yield chunk
        except S3Error as e:
            if e.code == "NoSuchKey":
                return
            raise
        finally:
            if response:
                response.close()
                response.release_conn()


class S3StorageService(ObjectStorageService):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        region: Optional[str] = None,
    ):
        self.client: S3Client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(
                signature_version="s3v4",
                connect_timeout=5,
                read_timeout=5,
                retries={
                    "max_attempts": 5,
                    "mode": "standard",
                },
            ),
        )

    def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError as e:
            if e.response["Error"]["Code"] not in ("404", "NoSuchBucket"):
                raise

        kwargs = {
            "Bucket": bucket,
            "Key": object_name,
            "Body": data,
        }

        if content_type is not None:
            kwargs["ContentType"] = content_type

        if metadata:
            kwargs["Metadata"] = metadata

        self.client.put_object(**kwargs)

    def get_object(
        self,
        bucket: str,
        object_name: str,
        chunk_size: int = 8192,
    ) -> Iterator[bytes]:
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError as e:
            if e.response["Error"]["Code"] not in ("404", "NoSuchBucket"):
                raise

        try:
            resp = self.client.get_object(Bucket=bucket, Key=object_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return
            raise

        body = resp["Body"]
        try:
            for chunk in body.iter_chunks(chunk_size):
                yield chunk
        finally:
            body.close()


class RustFsStorageService(S3StorageService):
    def __init__(self, endpoint, access_key, secret_key, region=None):
        super().__init__(endpoint, access_key, secret_key, region)


def NewClient(**kwargs) -> ObjectStorageService:
    ossType = os.getenv("OSS_TYPE") or kwargs.pop("oss_type", None)
    if not ossType:
        raise RuntimeError("OSS_TYPE is required")

    eps = entry_points().select(group="storage")
    ossType = ossType.lower()
    if ossType not in eps.names:
        raise RuntimeError(
            f"Storage provider '{ossType}' not found. Available: {list(eps.names)}"
        )

    cls = eps[ossType].load()
    return cls(**kwargs)
