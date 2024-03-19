import logging
import requests
from azure.functions import HttpRequest, HttpResponse
from jose import jwt, jwk, JWTError
import json

def main(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the id_token from the request headers
    id_token = req.headers.get('Authorization')

    # If the id_token exists
    if id_token:
        try:
            # Fetch the JWKS from Azure B2C
            jwks_uri = 'https://azresume.b2clogin.com/azresume.onmicrosoft.com/B2C_1_SignUpSignIn/discovery/v2.0/keys'
            response = requests.get(jwks_uri)
            jwks = response.json()

            # Get the header of the JWT
            headers = jwt.get_unverified_header(id_token)

            # Find the key in the JWKS that matches the kid in the JWT header
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

            # Verify the id_token and extract the claims
            token_claims = jwt.decode(id_token, rsa_key, algorithms=['RS256'])

            # If the extension_CanEdit claim is "1", return a response indicating that the user has admin rights
            if token_claims.get('extension_CanEdit') == "1":
                return HttpResponse(json.dumps({"admin": True}), status_code=200, mimetype="application/json")
        except JWTError:
            pass

    # If the id_token does not exist or the extension_CanEdit claim is not "1", return a response indicating that the user does not have admin rights
    return HttpResponse(json.dumps({"admin": False}), status_code=200, mimetype="application/json")