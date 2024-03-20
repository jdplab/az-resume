import os
import json
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timezone, timedelta
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
        last_post_blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), 'last_post_number.txt')
        last_post_number = int(last_post_blob_client.download_blob().readall())
        posts = []
        for i in range(last_post_number, max(0, last_post_number - 10), -1):
            post_id = str(i).zfill(4)
            blob_client = blob_service_client.get_blob_client(os.getenv('BLOGPOSTS_CONTAINER'), post_id + '.json')
            json_data = json.loads(blob_client.download_blob().readall())
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

            posts.append({'id': post_id, 'data': json_data, 'image_url': image_url})
        return func.HttpResponse(json.dumps(posts), status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)