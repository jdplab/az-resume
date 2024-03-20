import logging
import http.client
from azure.functions import HttpRequest, HttpResponse
from jose import jwt, JWTError
import json

def main(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    id_token = req.headers.get('Authorization')

    if id_token:
        try:
            logging.info('ID token found in request headers.')

            jwks_uri = 'azresume.b2clogin.com'
            conn = http.client.HTTPSConnection(jwks_uri)
            conn.request("GET", "/azresume.onmicrosoft.com/B2C_1_SignUpSignIn/discovery/v2.0/keys")
            response = conn.getresponse()
            jwks = json.loads(response.read().decode())

            logging.info('Retrieved JWKS: %s', jwks)

            headers = jwt.get_unverified_header(id_token)

            logging.info('JWT headers: %s', headers)

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

            logging.info('RSA key: %s', rsa_key)

            token_claims = jwt.decode(id_token, rsa_key, algorithms=['RS256'])

            logging.info('Token claims: %s', token_claims)

            if token_claims.get('extension_CanEdit') == "1":
                logging.info('User has admin rights.')
                return HttpResponse(json.dumps({"admin": True}), status_code=200, mimetype="application/json")
        except JWTError as e:
            logging.error('Error while decoding JWT: %s', e)
            pass
    else:
        logging.info('ID token not found in request headers.')
    logging.info('User does not have admin rights.')
    return HttpResponse(json.dumps({"admin": False}), status_code=200, mimetype="application/json")