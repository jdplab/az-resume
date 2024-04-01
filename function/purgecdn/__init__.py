import os
import logging
from azure.mgmt.cdn import CdnManagementClient
from azure.identity import DefaultAzureCredential
import azure.functions as func
from azure.core.exceptions import AzureError

def purge_cdn():
    try:
        credential = DefaultAzureCredential()
        cdn_client = CdnManagementClient(credential, os.getenv('SUBSCRIPTION_ID'))
        cdn_client.endpoints.begin_purge_content(
            os.getenv('RESOURCE_GROUP_NAME'),
            os.getenv('PROFILE_NAME'),
            os.getenv('ENDPOINT_NAME'),
            {"content_paths": ["/posts/*"]}
        )
    except AzureError as e:
        logging.error(f"Error purging CDN: {str(e)}")

def main(posts: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {posts.name}\n"
                 f"Blob Size: {posts.length} bytes")
    purge_cdn()