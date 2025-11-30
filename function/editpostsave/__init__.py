import azure.functions as func
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient
import os
import json
from verifytoken import verify_token
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared_code.cache_utils import invalidate_cache

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
                            title = req.form.get('title')
                            description = req.form.get('description')
                            html = req.form.get('html')
                            tags = req.form.get('tags')
                            post = container.read_item(item=post_id, partition_key=post_id)
                            post['title'] = title
                            post['description'] = description
                            post['html'] = html
                            post['tags'] = tags
                            container.upsert_item(body=post)

                            # Invalidate posts cache since we edited a post
                            try:
                                blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
                                blog_container = blob_service_client.get_container_client(os.getenv('BLOGPOSTS_CONTAINER'))
                                invalidate_cache(blog_container, 'posts')
                            except Exception as cache_error:
                                # Log but don't fail - cache invalidation is not critical
                                pass

                        except cosmos_exceptions.CosmosResourceNotFoundError:
                            return func.HttpResponse("Post not found", status_code=404)
                        except AzureError as e:
                            return func.HttpResponse(f"Error connecting to Cosmos DB: {str(e)}", status_code=500)
                        return func.HttpResponse("Edit saved successfully.", status_code=200)
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