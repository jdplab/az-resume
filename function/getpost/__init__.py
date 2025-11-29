import azure.functions as func
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.core.exceptions import AzureError
from datetime import datetime, timezone, timedelta
import os
import json

def extract_account_key(connection_string):
    """Extract AccountKey from Azure Storage connection string"""
    for part in connection_string.split(';'):
        if part.startswith('AccountKey='):
            return part.split('=', 1)[1]
    return None

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        post_id = req.params.get('id')
        if post_id:
            try:
                cosmos_client = CosmosClient.from_connection_string(os.getenv('resumedb1_DOCUMENTDB'))
                database = cosmos_client.get_database_client('resumedb')
                container = database.get_container_client('blogposts')
                post = container.read_item(item=post_id, partition_key=post_id)
            except cosmos_exceptions.CosmosResourceNotFoundError:
                return func.HttpResponse("Post not found", status_code=404)
            except AzureError as e:
                return func.HttpResponse(f"Error connecting to Cosmos DB: {str(e)}", status_code=500)

            try:
                storage_conn_string = os.getenv('STORAGE_CONNECTIONSTRING')
                blob_service_client = BlobServiceClient.from_connection_string(storage_conn_string)
                account_key = extract_account_key(storage_conn_string)
                image_blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), post_id + '.jpg')

                sas_token = generate_blob_sas(
                    blob_service_client.account_name,
                    os.getenv('BLOGPOSTS_CONTAINER'),
                    image_blob_client.blob_name,
                    account_key=account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.now(timezone.utc) + timedelta(minutes=30)
                )

                image_url = image_blob_client.url + "?" + sas_token
            except AzureError as e:
                return func.HttpResponse(f"Error generating image URL: {str(e)}", status_code=500)

            return func.HttpResponse(json.dumps({'data': post, 'image_url': image_url}), status_code=200)
        else:
            return func.HttpResponse("No id provided", status_code=400)
    except Exception as e:
        return func.HttpResponse(f"Unexpected error: {str(e)}", status_code=500)