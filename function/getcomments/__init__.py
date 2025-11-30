import azure.functions as func
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient
import os
import json
import logging
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared_code.cache_utils import get_cached_data, save_cached_data

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        post_id = req.params.get('id')
        if post_id:
            # Try to get cached comments first
            try:
                blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
                blog_container = blob_service_client.get_container_client(os.getenv('BLOGPOSTS_CONTAINER'))

                cache_key = f'comments-{post_id}'
                cached_comments = get_cached_data(blog_container, cache_key)

                if cached_comments is not None:
                    comments = cached_comments
                else:
                    # Cache miss - query CosmosDB
                    cosmos_client = CosmosClient.from_connection_string(os.getenv('resumedb1_DOCUMENTDB'))
                    database = cosmos_client.get_database_client('resumedb')
                    container = database.get_container_client('comments')
                    query = "SELECT * FROM c WHERE c.post_id = @post_id ORDER BY c.timestamp DESC"
                    parameters = [{"name": "@post_id", "value": post_id}]
                    comments = list(container.query_items(
                        query=query,
                        parameters=parameters,
                        enable_cross_partition_query=True
                    ))
                    # Save to cache for next request
                    save_cached_data(blog_container, cache_key, comments)

            except cosmos_exceptions.CosmosResourceNotFoundError:
                logging.error("Comments not found")
                return func.HttpResponse("Error processing request", status_code=404)
            except AzureError as e:
                logging.error(f"Error connecting to Cosmos DB: {str(e)}")
                return func.HttpResponse("Error processing request", status_code=500)
            return func.HttpResponse(json.dumps(comments), status_code=200, headers={"Content-Type": "application/json"})
        else:
            return func.HttpResponse("No id provided", status_code=400)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse("Error processing request", status_code=500)