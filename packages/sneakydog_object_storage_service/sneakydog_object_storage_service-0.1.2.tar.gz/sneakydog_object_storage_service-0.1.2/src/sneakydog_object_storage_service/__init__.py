import asyncio
import os
import shutil
from abc import ABC, abstractmethod
from importlib.metadata import entry_points
from typing import AsyncIterator, BinaryIO, Dict, Optional, Type

import aioboto3
import aiofiles
from botocore.client import Config
from mypy_boto3_s3 import S3Client

__all__ = [
    "AsyncObjectStorageService",
    "NewInstance",
]


class AsyncObjectStorageService(ABC):
    @abstractmethod
    async def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str: ...

    @abstractmethod
    async def get_object(
        self, bucket: str, object_name: str, chunk_size: int = 2048
    ) -> AsyncIterator[bytes]: ...


class AsyncLocalStorageService(AsyncObjectStorageService):
    def __init__(self, root: str):
        self.root = os.path.abspath(root)

    def _path(self, bucket: str, object_name: str) -> str:
        return os.path.join(self.root, bucket, object_name)

    async def put_object(
        self,
        *,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        path = self._path(bucket, object_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        await asyncio.to_thread(
            shutil.copyfileobj,
            data,
            open(path, "wb"),
        )

        return path

    async def get_object(
        self,
        *,
        bucket: str,
        object_name: str,
        chunk_size: int = 2048,
    ) -> AsyncIterator[bytes]:
        path = self._path(bucket, object_name)

        async def stream():
            async with aiofiles.open(path, "rb") as f:
                while chunk := await f.read(chunk_size):
                    if chunk:
                        yield chunk

        return stream()


class AsyncS3StorageService(AsyncObjectStorageService):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        region: str = None,
        ssl: bool = False,
    ):
        self.session = aioboto3.Session()
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.ssl = ssl

    async def _client(self) -> S3Client:
        return self.session.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            use_ssl=self.ssl,
            config=Config(
                retries={"max_attempts": 1},
                connect_timeout=3,
                read_timeout=10,
            ),
        )

    async def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        s3: S3Client
        async with await self._client() as s3:
            await s3.upload_fileobj(
                data,
                bucket,
                object_name,
                ExtraArgs={
                    "ContentType": content_type or "application/octet-stream",
                    "Metadata": metadata or {},
                },
            )

            return object_name

    async def get_object(
        self, bucket: str, object_name: str, chunk_size: int = 8192
    ) -> AsyncIterator[bytes]:
        async def stream():
            s3: S3Client
            async with await self._client() as s3:
                response = await s3.get_object(Bucket=bucket, Key=object_name)
                body = response["Body"]  # type: ignore # type: StreamingBody
                async for chunk in body.iter_chunks(chunk_size=chunk_size):
                    if chunk:
                        yield chunk

        return stream()


class AsyncRustFSStorageService(AsyncObjectStorageService):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        region: str = None,
        ssl: bool = False,
    ):
        self.session = aioboto3.Session()
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.ssl = ssl

    async def _client(self) -> S3Client:
        return self.session.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="us-east-1",
            use_ssl=self.ssl,
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 1},
                connect_timeout=3,
                read_timeout=10,
            ),
        )

    async def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        s3: S3Client
        async with await self._client() as s3:
            await s3.upload_fileobj(
                data,
                bucket,
                object_name,
                ExtraArgs={
                    "ContentType": content_type or "application/octet-stream",
                    "Metadata": metadata or {},
                },
            )

            return object_name

    async def get_object(
        self, bucket: str, object_name: str, chunk_size: int = 8192
    ) -> AsyncIterator[bytes]:
        async def stream():
            s3: S3Client
            async with await self._client() as s3:
                response = await s3.get_object(Bucket=bucket, Key=object_name)
                body = response["Body"]  # type: ignore # type: StreamingBody
                async for chunk in body.iter_chunks(chunk_size=chunk_size):
                    if chunk:
                        yield chunk

        return stream()


def NewInstance(**kwargs) -> AsyncObjectStorageService:
    ossType = os.getenv("OSS_TYPE") or kwargs.pop("oss_type", None)
    if not ossType:
        raise RuntimeError(
            "OSS_TYPE is required. "
            "Set environment variable OSS_TYPE or pass oss_type=..."
        )

    ossType = ossType.lower()
    eps = entry_points(group="storage")
    if ossType not in eps.names:
        raise RuntimeError(
            f"Storage provider '{ossType}' not found. Available: {list(eps.names)}"
        )

    cls: Type[AsyncObjectStorageService] = eps[ossType].load()
    return cls(**kwargs)
