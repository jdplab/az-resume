import logging
import json
import azure.functions as func
    
    def main(req: func.HttpRequest, sendGridMessage: func.Out[str]) -> func.HttpResponse:
        logging.info('SendEmail function processed a request.')
    
        try:
            req_body = req.get_json()
        except ValueError:
            logging.error('Invalid request body')
            return func.HttpResponse('Invalid request body', status_code=400)
    
        name = req_body.get('name')
        email = req_body.get('email')
        message = req_body.get('message')
    
        if not name or not email or not message:
            logging.error('Missing required fields')
            return func.HttpResponse('Missing required fields', status_code=400)
    
        sender_email = 'jon@jon-polansky.com'
        recipient_email = 'jon@jon-polansky.com'
        subject = 'Jon-Polansky.com Form Submission'
    
        email_content = f"""
        Name: {name}
        Email: {email}
        Message: {message}
        """
    
        try:
            sendGridMessage.set(json.dumps({
                "personalizations": [{"to": [{"email": recipient_email}]}],
                "from": {"email": sender_email},
                "subject": subject,
                "content": [{"type": "text/plain", "value": email_content}]
            }))
        except Exception as e:
            logging.error(f'Error sending email: {str(e)}')
            return func.HttpResponse('Error sending email', status_code=500)
    
        logging.info('Email sent successfully')
        return func.HttpResponse('Email sent successfully', status_code=200)
    