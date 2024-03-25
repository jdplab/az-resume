import logging
import http.client
from azure.functions import HttpRequest, HttpResponse
from jose import jwt, JWTError
import json

def get_jwks():
    jwks_uri = 'azresume.b2clogin.com'
    conn = http.client.HTTPSConnection(jwks_uri)
    conn.request("GET", "/azresume.onmicrosoft.com/B2C_1_SignUpSignIn/discovery/v2.0/keys")
    response = conn.getresponse()
    return json.loads(response.read().decode())

def verify_token(id_token):
    jwks = get_jwks()
    headers = jwt.get_unverified_header(id_token)
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == headers['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    expected_audience = '8437bac7-4641-445c-83f2-20a4105108b5'
    token_claims = jwt.decode(id_token, rsa_key, algorithms=['RS256'], audience=expected_audience)
    return token_claims

def main(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        auth_header = req.headers.get('Authorization')
        id_token = auth_header.split(' ')[1]
        if id_token:
            try:
                logging.info('ID token found in request headers.')
                token_claims = verify_token(id_token)
            except Exception as e:
                logging.error(f'Error verifying token: {str(e)}')
                return HttpResponse(f"Error verifying token: {str(e)}", status_code=400)
            if token_claims.get('extension_CanEdit') == "1":
                logging.info('User has admin rights.')
                return HttpResponse(json.dumps({"admin": True}), status_code=200, mimetype="application/json")
            else:
                logging.info('User is not an admin.')
                return HttpResponse(json.dumps("admin": False), status_code=200, mimetype="application/json")
        else:
            logging.info('ID token not found in request headers.')
            return HttpResponse("No Authorization header provided", status_code=401)
    except Exception as e:
        logging.error(f'An unexpected error occurred: {str(e)}')
        return HttpResponse(f"Unexpected error: {str(e)}", status_code=500)