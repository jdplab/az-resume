import azure.functions as func
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.core.exceptions import AzureError
import os
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        post_id = req.params.get('id')
        if post_id:
            try:
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