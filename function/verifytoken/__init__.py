import logging
import http.client
from azure.functions import HttpRequest, HttpResponse
from libs import jose
import json

jwt = jose.jwt
JWTError = jose.JWTError

def main(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    id_token = req.headers.get('Authorization')

    if id_token:
        try:
            jwks_uri = 'azresume.b2clogin.com'
            conn = http.client.HTTPSConnection(jwks_uri)
            conn.request("GET", "/azresume.onmicrosoft.com/B2C_1_SignUpSignIn/discovery/v2.0/keys")
            response = conn.getresponse()
            jwks = json.loads(response.read().decode())

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

            token_claims = jwt.decode(id_token, rsa_key, algorithms=['RS256'])

            if token_claims.get('extension_CanEdit') == "1":
                return HttpResponse(json.dumps({"admin": True}), status_code=200, mimetype="application/json")
        except JWTError:
            pass

    return HttpResponse(json.dumps({"admin": False}), status_code=200, mimetype="application/json")