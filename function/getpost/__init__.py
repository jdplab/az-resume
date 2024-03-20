import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        post_id = req.params.get('id')
        if post_id:
            blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
            blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), post_id + '.json')
            json_data = json.loads(blob_client.download_blob().readall())
            image_blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), post_id + '.jpg')
            image_url = image_blob_client.url
            return func.HttpResponse(json.dumps({'data': json_data, 'image_url': image_url}), status_code=200)
        else:
            return func.HttpResponse("No id provided", status_code=400)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)