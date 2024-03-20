import azure.functions as func
from azure.storage.blob import BlobServiceClient
import uuid
import json
import os
from verifytoken import verify_token  # Import the verify_token function

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        auth_header = req.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            # Verify the JWT
            payload = verify_token(token)
            if payload.get('extension_CanEdit') == "1":
                # Get the title, description, and HTML from the request body
                req_body = req.get_json()
                title = req_body.get('title')
                description = req_body.get('description')
                html = req_body.get('html')
                # Save these properties as a new blob
                blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
                blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), str(uuid.uuid4()) + '.json')
                blob_client.upload_blob(json.dumps({'title': title, 'description': description, 'html': html}))
                return func.HttpResponse("Post saved successfully", status_code=200)
            else:
                return func.HttpResponse("Access Denied", status_code=403)
        else:
            return func.HttpResponse("No Authorization header provided", status_code=401)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)