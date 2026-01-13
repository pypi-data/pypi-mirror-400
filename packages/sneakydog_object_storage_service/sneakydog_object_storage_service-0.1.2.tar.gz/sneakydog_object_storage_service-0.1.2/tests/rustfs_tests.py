import asyncio
# import shutil
from typing import Type

import aiofiles

import sneakydog_object_storage_service as SOSS

# minioadmin

oss: Type[SOSS.AsyncObjectStorageService] = SOSS.NewInstance(
    oss_type="rustFS",
    endpoint="https://play.rustfs.com:9000",
    access_key="qyCiNa2APXTVrmKk1peI",
    secret_key="gVq4f20WoXUHSM1u9Qn5CdkhpLDyKI6wNJO7Bemv",
    region="my-region",
    ssl=True,
)


async def main():
    with open("C:\\Users\\fz_dong\\Pictures\\The-Dark-Knight.png", "rb") as f:
        await oss.put_object(
            bucket="dddddddddddddd",
            object_name="test23.jpg",
            data=f,
        )

    stream = await oss.get_object(bucket="dddddddddddddd", object_name="Mickey_Who.png")
    async with aiofiles.open("./tests/Mickey_Who.png", "wb") as f:
        async for chunk in stream:
            await f.write(chunk)


asyncio.run(main())
