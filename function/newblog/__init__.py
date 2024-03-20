import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from datetime import datetime, timezone, timedelta
from verifytoken import verify_token
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request...')
    try:
        auth_header = req.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            # Verify the JWT
            payload = verify_token(token)
            if payload.get('extension_CanEdit') == "1":
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
                logging.info('SAS token generated successfully')
                logging.info(f'Blob URL with SAS: {blob_url_with_sas}')
                return func.HttpResponse(blob_url_with_sas, status_code=200)
            else:
                logging.warning('Access denied: user is not an admin')
                return func.HttpResponse("Access Denied", status_code=403)
        else:
            logging.warning('No Authorization header provided')
            return func.HttpResponse("No Authorization header provided", status_code=401)
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return func.HttpResponse(str(e), status_code=400)