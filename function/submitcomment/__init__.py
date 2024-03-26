import azure.functions as func
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.core.exceptions import AzureError
import os
import uuid
from datetime import datetime
from verifytoken import verify_token
import logging
import pytz
import re

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        auth_header = req.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            # Verify the JWT
            try:
                token_claims = verify_token(token)
            except Exception as e:
                logging.error(f"Error verifying token: {str(e)}")
                return func.HttpResponse("Error processing request", status_code=400)
            # Set token_claims as user info
            firstname = token_claims.get('given_name')
            lastname = token_claims.get('family_name')
            post_id = req.params.get('id')
            comment = req.form.get('comment')
            comment = re.sub(r'[^\w\s.,!?;:]', '', comment)
            if not post_id:
                return func.HttpResponse("Missing post id", status_code=400)
            if not comment:
                return func.HttpResponse("Missing comment", status_code=400)
            if comment.strip() == '':
                return func.HttpResponse("Comment cannot be empty", status_code=400)
            try:
                cosmos_client = CosmosClient.from_connection_string(os.getenv('resumedb1_DOCUMENTDB'))
                database = cosmos_client.get_database_client('resumedb')
                container = database.get_container_client('comments')
                # Get the current timestamp
                now_utc = datetime.now(pytz.timezone('UTC'))
                now_est = now_utc.astimezone(pytz.timezone('US/Eastern'))
                timestamp = now_est.isoformat()
                # Create a new comment object
                new_comment = {'id': str(uuid.uuid4()), 'post_id': post_id, 'comment': comment, 'timestamp': timestamp, 'firstname': firstname, 'lastname': lastname}
                # Save the comment to CosmosDB
                container.upsert_item(new_comment)
            except cosmos_exceptions.CosmosResourceNotFoundError:
                logging.error("Post not found")
                return func.HttpResponse("Error processing request", status_code=404)
            except AzureError as e:
                logging.error(f"Error connecting to Cosmos DB: {str(e)}")
                return func.HttpResponse("Error processing request", status_code=500)
            return func.HttpResponse("Comment saved successfully", status_code=200)
        else:
            return func.HttpResponse("No Authorization header provided", status_code=401)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse("Error processing request", status_code=500)