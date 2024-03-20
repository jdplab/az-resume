import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from datetime import datetime, timezone, timedelta
from verifytoken import verify_token
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        auth_header = req.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            # Verify the JWT
            payload = verify_token(token)
            if 'admin' in payload and payload['admin']:
                # Generate a SAS for the blob
                blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_CONNECTIONSTRING'))
                blob_client = blob_service_client.get_blob_client('admin', 'newblog.html')
                sas_token = generate_blob_sas(
                    blob_service_client.account_name,
                    blob_client.container_name,
                    blob_client.blob_name,
                    account_key=blob_service_client.credential.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.now(timezone.utc) + timedelta(hours=1)
                )
                blob_url_with_sas = f"https://{blob_service_client.account_name}.blob.core.windows.net/{blob_client.container_name}/{blob_client.blob_name}?{sas_token}"
                return func.HttpResponse(blob_url_with_sas, status_code=200)
            else:
                return func.HttpResponse("Access Denied", status_code=403)
        else:
            return func.HttpResponse("No Authorization header provided", status_code=401)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=400)