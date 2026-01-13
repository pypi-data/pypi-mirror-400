import asyncio

import sneakydog_object_storage_service as SOSS

# minioadmin

ossClient = SOSS.NewClient(
    oss_type="minio",
    endpoint="play.minio.io:9000",
    access_key="Q3AM3UQ867SPQQA43P2F",
    secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
    region="us-east-1",
    ssl=True,
)


def putObject():
    with open("C:\\Users\\fz_dong\\Pictures\\The-Dark-Knight.png", "rb") as f:
        ossClient.put_object(
            bucket="hello",
            object_name="test23.jpg",
            data=f,
        )


def getObject():
    chunks = ossClient.get_object(bucket="hello", object_name="test23.jpg")
    with open("./Mickey_Who.png", "wb") as f:
        for chunk in chunks:
            f.write(chunk)


async def main():
    await asyncio.to_thread(putObject)
    await asyncio.to_thread(getObject)


asyncio.run(main())
