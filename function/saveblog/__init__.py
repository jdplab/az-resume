import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.core.exceptions import AzureError
import os
from datetime import datetime
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
                # Get the title, description, html, image, and tags from the form data
                title = req.form.get('title')
                description = req.form.get('description')
                html = req.form.get('html')
                image = req.files.get('image')
                tags = [tag.strip() for tag in req.form.get('tags').split(',')]
                # Get the last post number from Cosmos DB
                try:
                    cosmos_client = CosmosClient.from_connection_string(os.getenv('resumedb1_DOCUMENTDB'))
                    database = cosmos_client.get_database_client('resumedb')
                    container = database.get_container_client('blogposts')
                    last_post_number = container.read_item(item='last_post_number', partition_key='last_post_number')['value']
                except cosmos_exceptions.CosmosResourceNotFoundError:
                    last_post_number = 0
                except AzureError as e:
                    return func.HttpResponse(f"Error connecting to Cosmos DB: {str(e)}", status_code=500)
                # Increment the post number and format it as a 4-digit string
                post_id = str((last_post_number + 1).zfill(4))
                # Update the last post number in Cosmos DB
                container.upsert_item({'id': 'last_post_number', 'value': post_id})
                # Get the current timestamp
                timestamp = datetime.now().isoformat()
                # Save these properties as a new item in Cosmos DB
                container.upsert_item({'id': post_id, 'title': title, 'description': description, 'html': html, 'tags': tags, 'timestamp': timestamp})
                if image:
                    # Save the image in Blob Storage
                    try:
                        blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
                        image_blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), post_id + '.jpg')
                        image_blob_client.upload_blob(image)
                    except AzureError as e:
                        return func.HttpResponse(f"Error uploading image to Blob Storage: {str(e)}", status_code=500)
                return func.HttpResponse("Post saved successfully", status_code=200)
            else:
                return func.HttpResponse("Access Denied", status_code=403)
        else:
            return func.HttpResponse("No Authorization header provided", status_code=401)
    except Exception as e:
        return func.HttpResponse(f"Unexpected error: {str(e)}", status_code=500)