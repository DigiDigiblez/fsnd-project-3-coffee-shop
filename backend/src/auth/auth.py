import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'fsnd2020.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'cafe'

CODE = {
    # Success codes
    "200_OK": 200,

    # Client error codes
    "401_UNAUTHORIZED": 401,
    "403_FORBIDDEN": 403,

    # Server error codes
    "500_INTERNAL_SERVER_ERROR": 500
}

ERR = {
    CODE["401_UNAUTHORIZED"]: {
        "Type": "AuthError",
        "Title": "invalid_header",
        "Code": CODE["401_UNAUTHORIZED"],
    }
}


# AuthError Exception: A standardised way to communicate auth failure modes
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Handles the raising of errors
def raise_error(err, err_desc: str):
    if err["Type"] == "AuthError":
        raise AuthError({
            "code": err["Title"],
            "description": err_desc
        }, err["Code"])


# Retrieve token from auth header
def get_token_auth_header():
    if "Authorization" not in request.headers:
        # Raise a 401 error
        raise_error(ERR[CODE["401_UNAUTHORIZED"]], "Authorization header is missing")

    # Dissect header
    header_parts = request.headers['Authorization'].split()
    bearer_prefix = header_parts[0]
    auth_token = header_parts[1]

    # 401 err handling
    if not bearer_prefix:
        raise_error(ERR[CODE["401_UNAUTHORIZED"]], "Authorization header is missing bearer prefix")

    elif bearer_prefix and len(header_parts) == 1:
        raise_error(ERR[CODE["401_UNAUTHORIZED"]], "Authorization header is missing auth token")

    elif len(header_parts) > 2:
        raise_error(ERR[CODE["401_UNAUTHORIZED"]], "Authorization header is malformed")

    return auth_token


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    raise Exception('Not Implemented')


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    raise Exception('Not Implemented')


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
