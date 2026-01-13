import asyncio

# import shutil
from typing import Type


import sneakydog_object_storage_service as SOSS

# minioadmin

ossClient = SOSS.NewClient(
    oss_type="rustFS",
    endpoint="https://play.rustfs.com",
    access_key="qyCiNa2APXTVrmKk1peI",
    secret_key="gVq4f20WoXUHSM1u9Qn5CdkhpLDyKI6wNJO7Bemv",
    region="my-region",
)


def putObject():
    with open("C:\\Users\\fz_dong\\Pictures\\The-Dark-Knight.png", "rb") as f:
        ossClient.put_object(
            bucket="hahahahaha",
            object_name="test23.jpg",
            data=f,
        )


def getObject():
    chunks = ossClient.get_object(bucket="hahahahaha", object_name="test23.jpg")
    with open("./Mickey_Who.png", "wb") as f:
        for chunk in chunks:
            f.write(chunk)



async def main():
    await asyncio.to_thread(putObject)
    # await asyncio.to_thread(getObject)


asyncio.run(main())
