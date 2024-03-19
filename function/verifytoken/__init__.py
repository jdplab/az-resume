import logging
import http.client
from azure.functions import HttpRequest, HttpResponse
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import jwt
import json
import base64

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

            public_key = rsa.RSAPublicNumbers(
                e=int.from_bytes(base64.urlsafe_b64decode(rsa_key['e'] + '=='), byteorder='big'),
                n=int.from_bytes(base64.urlsafe_b64decode(rsa_key['n'] + '=='), byteorder='big')
            ).public_key(default_backend())

            token_claims = jwt.decode(id_token, public_key, algorithms=['RS256'])

            if token_claims.get('extension_CanEdit') == "1":
                return HttpResponse(json.dumps({"admin": True}), status_code=200, mimetype="application/json")
        except jwt.JWTError:
            pass

    return HttpResponse(json.dumps({"admin": False}), status_code=200, mimetype="application/json")