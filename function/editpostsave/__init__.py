import azure.functions as func
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.core.exceptions import AzureError
from datetime import datetime, timezone, timedelta
import os
import json
from verifytoken import verify_token

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        auth_header = req.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            # Verify the JWT
            try:
                payload = verify_token(token)
            except Exception as e:
                return func.HttpResponse(f"Error verifying token: {str(e)}", status_code=400)
            if payload.get('extension_CanEdit') == "1":
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
                        return func.HttpResponse(json.dumps(post), status_code=200)
                    else:
                        return func.HttpResponse("No id provided", status_code=400)
                except Exception as e:
                    return func.HttpResponse(f"Unexpected error: {str(e)}", status_code=500)
            else:
                return func.HttpResponse("Access Denied", status_code=403)
        else:
            return func.HttpResponse("No Authorization header provided", status_code=401)
    except Exception as e:
        return func.HttpResponse(f"Unexpected error: {str(e)}", status_code=500)