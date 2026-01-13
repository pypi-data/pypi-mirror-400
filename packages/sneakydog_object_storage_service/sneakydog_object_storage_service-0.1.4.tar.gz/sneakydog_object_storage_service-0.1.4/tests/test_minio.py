from minio import Minio
import urllib3


# Create client with anonymous access.
# client = Minio("play.min.io")

# # Create client with access and secret key.
# client = Minio("s3.amazonaws.com", "ACCESS-KEY", "SECRET-KEY")

# Create client with access key and secret key with specific region.
client = Minio(
    "play.minio.io:9000",
    access_key="Q3AM3UQ867SPQQA43P2F",
    secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
    region="my-region",
)

buckets = client.list_buckets()
for bucket in buckets:
    print(bucket.name, bucket.creation_date)
    
# Create client with custom HTTP client using proxy server.

# client = Minio(
#     "SERVER:PORT",
#     access_key="ACCESS_KEY",
#     secret_key="SECRET_KEY",
#     secure=True,
#     http_client=urllib3.ProxyManager(
#         "https://PROXYSERVER:PROXYPORT/",
#         timeout=urllib3.Timeout.DEFAULT_TIMEOUT,
#         cert_reqs="CERT_REQUIRED",
#         retries=urllib3.Retry(
#             total=5,
#             backoff_factor=0.2,
#             status_forcelist=[500, 502, 503, 504],
#         ),
#     ),
# )