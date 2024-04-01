from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.core.exceptions import AzureError
import azure.functions as func
from verifytoken import verify_token
import os

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
                            post_container = database.get_container_client('blogposts')
                            comment_container = database.get_container_client('comments')

                            # Delete the post
                            post_container.delete_item(item=post_id, partition_key=post_id)

                            # Check and delete the associated comments
                            query = "SELECT * FROM c WHERE c.post_id = @post_id"
                            parameters = [{"name": "@post_id", "value": post_id}]
                            comments = list(comment_container.query_items(
                                query=query,
                                parameters=parameters,
                                enable_cross_partition_query=True
                            ))
                            if comments:
                                for comment in comments:
                                    comment_container.delete_item(item=comment['id'], partition_key=comment['id'])
                        except cosmos_exceptions.CosmosResourceNotFoundError:
                            return func.HttpResponse("Post or comments not found", status_code=404)
                        except AzureError as e:
                            return func.HttpResponse(f"Error connecting to Cosmos DB: {str(e)}", status_code=500)

                        try:
                            # Delete the image
                            blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
                            image_blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), post_id + '.jpg')
                            image_blob_client.delete_blob()

                            # Delete the HTML file
                            html_blob_client = blob_service_client.get_blob_client(os.getenv('WEB_CONTAINER'), 'posts/' + post_id + '.html')
                            html_blob_client.delete_blob()
                        except AzureError as e:
                            return func.HttpResponse(f"Error deleting image: {str(e)}", status_code=500)

                        # Return a success response
                        return func.HttpResponse("Post, image and associated comments deleted successfully", status_code=200)
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