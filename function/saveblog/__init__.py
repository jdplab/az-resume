import azure.functions as func
from azure.storage.blob import BlobServiceClient
import json
import os
from datetime import datetime
from verifytoken import verify_token  # Import the verify_token function

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        auth_header = req.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            # Verify the JWT
            payload = verify_token(token)
            if payload.get('extension_CanEdit') == "1":
                # Get the title, description, html, image, and tags from the form data
                title = req.form.get('title')
                description = req.form.get('description')
                html = req.form.get('html')
                image = req.files.get('image')
                tags = [tag.strip() for tag in req.form.get('tags').split(',')]
                # Get the last post number from a blob
                blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
                last_post_blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), 'last_post_number.txt')
                last_post_number = int(last_post_blob_client.download_blob().readall())
                # Increment the post number and format it as a 4-digit string
                post_id = str(last_post_number + 1).zfill(4)
                # Update the last post number blob
                last_post_blob_client.upload_blob(post_id, overwrite=True)
                # Get the current timestamp
                timestamp = datetime.now().isoformat()
                # Save these properties as a new blob
                blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), post_id + '.json')
                blob_client.upload_blob(json.dumps({'title': title, 'description': description, 'html': html, 'tags': tags, 'timestamp': timestamp}))
                if image:
                    image_blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), post_id + '.jpg')
                    image_blob_client.upload_blob(image)
                return func.HttpResponse("Post saved successfully", status_code=200)
            else:
                return func.HttpResponse("Access Denied", status_code=403)
        else:
            return func.HttpResponse("No Authorization header provided", status_code=401)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)