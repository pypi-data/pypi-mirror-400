import asyncio
from typing import Type

import aiofiles

from sneakydog_object_storage_service import ObjectStorageService, NewClient

oss: Type[ObjectStorageService] = NewClient(oss_type="local", root="./tests")


async def main():
    # with open("C:\\Users\\fz_dong\\Pictures\\The-Dark-Knight.png", "rb") as f:
    #     await oss.put_object(
    #         bucket="testfiles",
    #         object_name="test2.jpg",
    #         data=f,
    #     )

    stream = await oss.get_object(bucket="dddddddddddddd", object_name="test.jpg")
    async with aiofiles.open("./tests/test33.jpg", "wb") as f:
        async for chunk in stream:
            await f.write(chunk)
        # res = await oss.download(bucket="testfiles", object_name="test.jpg")


asyncio.run(main())
