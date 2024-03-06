import azure.functions as func
import logging
import json

def main(req: func.HttpRequest, inputDocument: func.DocumentList, outputDocument: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    ip_address = req.headers.get('X-Forwarded-For')
    if ip_address is None:
        raise Exception('X-Forwarded-For header not found in request')


    doc = next((doc for doc in inputDocument if doc['id'] == ip_address), None)

    if doc is None:
        logging.info('No visitors value found in CosmosDB for this IP. Creating it now.')
        data = {'id': ip_address, 'visits': 1}
    else:
        logging.info('Visitors value found in CosmosDB for this IP. Incrementing it now.')
        data = doc.to_dict()
        data['visits'] += 1

    unique_visitors = len(set(doc['id'] for doc in inputDocument))
    total_visits = sum(doc['visits'] for doc in inputDocument)

    outputDocument.set(func.Document.from_dict(data))

    result = {
        'unique_visitors': unique_visitors,
        'total_visits': total_visits,
        'visits': data['visits']
    }

    return func.HttpResponse(
        body=json.dumps(result),
        status_code=200,
        headers={'Content-Type': 'application/json'}
    )