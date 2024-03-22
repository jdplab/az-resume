import azure.functions as func
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.core.exceptions import AzureError
from datetime import datetime, timezone, timedelta
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos_client = CosmosClient.from_connection_string(os.getenv('resumedb1_DOCUMENTDB'))
        database = cosmos_client.get_database_client('resumedb')
        container = database.get_container_client('blogposts')
    except AzureError as e:
        return func.HttpResponse(f"Error connecting to Cosmos DB: {str(e)}", status_code=500)

    try:
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
    except AzureError as e:
        return func.HttpResponse(f"Error connecting to Blob Storage: {str(e)}", status_code=500)

    try:
        query = "SELECT * FROM c ORDER BY c.timestamp DESC OFFSET 0 LIMIT 10"
        posts = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
    except cosmos_exceptions.CosmosQueryError as e:
        return func.HttpResponse(f"Error querying Cosmos DB: {str(e)}", status_code=500)

    for post in posts:
        post_id = post['id']
        try:
            image_blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), post_id + '.jpg')
            sas_token = generate_blob_sas(
                blob_service_client.account_name,
                os.getenv('BLOGPOSTS_CONTAINER'),
                image_blob_client.blob_name,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc) + timedelta(minutes=20)
            )
            image_url = image_blob_client.url + "?" + sas_token
            post['image_url'] = image_url
        except AzureError as e:
            return func.HttpResponse(f"Error generating image URL: {str(e)}", status_code=500)

    return func.HttpResponse(json.dumps(posts), status_code=200)