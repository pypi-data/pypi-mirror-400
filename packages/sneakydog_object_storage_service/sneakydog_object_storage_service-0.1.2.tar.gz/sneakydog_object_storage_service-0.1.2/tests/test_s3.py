import asyncio
import shutil
from typing import Type

import aiofiles

import sneakydog_object_storage_service

# minioadmin

oss: Type[sneakydog_object_storage_service.AsyncObjectStorageService] = sneakydog_object_storage_service.NewInstance(
    oss_type="s3",
    endpoint="https://play.minio.io:9000",
    access_key="Q3AM3UQ867SPQQA43P2F",
    secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
    region="my-region",
    ssl=True,
)


async def main():
    # with open("C:\\Users\\fz_dong\\Pictures\\The-Dark-Knight.png", "rb") as f:
    #     await oss.put_object(
    #         bucket="dddddddddddddd",
    #         object_name="test2.jpg",
    #         data=f,
    #     )

    stream = await oss.get_object(bucket="dddddddddddddd", object_name="test2.jpg")
    async with aiofiles.open("./tests/test.jpg", "wb") as f:
        async for chunk in stream:
            await f.write(chunk)

asyncio.run(main())
