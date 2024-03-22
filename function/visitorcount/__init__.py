import azure.functions as func
import logging
import json

def main(req: func.HttpRequest, inputDocument: func.DocumentList, outputDocument: func.Out[func.Document]) -> func.HttpResponse:
    try:
        logging.info('Python HTTP trigger function processed a request.')
        xforwardedfor = req.headers.get('X-Forwarded-For')
        if not xforwardedfor:
            return func.HttpResponse("X-Forwarded-For header not found in request", status_code=400)
        ip_address = xforwardedfor.split(":")[0]

        repeatVisit = req.params.get('repeatVisit')

        doc = next((doc for doc in inputDocument if doc['id'] == ip_address), None)

        if doc is None:
            logging.info('No visitors value found in CosmosDB for this IP. Creating it now.')
            data = {'id': ip_address, 'visits': 1}
            inputDocument.append(data)
        else:
            logging.info('Visitors value found in CosmosDB for this IP.')
            data = doc.to_dict()
            if repeatVisit == "0":
                data['visits'] += 1
            for doc in inputDocument:
                if doc['id'] == ip_address:
                    doc['visits'] = data['visits']
                    break

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
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(
            body=f"An error occurred: {str(e)}",
            status_code=500
        )