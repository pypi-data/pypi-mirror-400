import random
import string
import base64
import time
import uuid
import json
import jwt
import logging
from math import floor
from jwt.utils import to_base64url_uint

import Cryptodome
from Cryptodome.PublicKey import (RSA, ECC)
from Cryptodome.Hash import SHA256
from Cryptodome.Signature import pkcs1_15


import django
from django.contrib.auth.backends import ModelBackend

try:
    from urlparse import parse_qs, urlsplit
except ImportError:
    from urllib.parse import parse_qs, urlsplit

from django.utils import timezone
from django.contrib.auth.models import User

from oidc_provider.models import (
    Client,
    Code,
    Token,
    ResponseType)

logger = logging.getLogger(__name__)

FAKE_NONCE = 'cb584e44c43ed6bd0bc2d9c7e242837d'
FAKE_RANDOM_STRING = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
FAKE_CODE_CHALLENGE = 'YlYXEqXuRm-Xgi2BOUiK50JW1KsGTX6F1TDnZSC8VTg'
FAKE_CODE_VERIFIER = 'SmxGa0XueyNh5bDgTcSrqzAh2_FmXEqU8kDT6CuXicw'

# avoid computation exenstive cost
FAKE_ECP256_PRIVKEY = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIHdm2ynC4Cn4uqTpQ1W5kikdxrcXEk8ESAsxXPH//epLoAoGCCqGSM49
AwEHoUQDQgAEq2Wk3s1RYzO4E0lDT9+7w7IYx9NFutAMbeZj+sb+tY0HdXC2VHYb
MoJk4VfoYCuLl8orNqgFYPa/WsctXAnwYQ==
-----END EC PRIVATE KEY-----"""

FAKE_RSA4096_PRIVKEY = """-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----"""


def create_fake_user():
    """
    Create a test user.

    Return a User object.
    """
    user = User()
    user.username = 'johndoe'
    user.email = 'johndoe@example.com'
    user.first_name = 'John'
    user.last_name = 'Doe'
    user.set_password('1234')

    user.save()

    return user


def create_fake_client(response_type, is_public=False, require_consent=True):
    """
    Create a test client, response_type argument MUST be:
    'code', 'id_token' or 'id_token token'.

    Return a Client object.
    """
    client = Client()
    client.name = 'Some Client'
    client.client_id = str(random.randint(1, 999999)).zfill(6)
    if is_public:
        client.client_type = 'public'
        client.client_secret = ''
    else:
        client.client_secret = str(random.randint(1, 999999)).zfill(6)
    client.redirect_uris = ['http://example.com/']
    client.require_consent = require_consent

    client.save()

    # check if response_type is a string in a python 2 and 3 compatible way
    if isinstance(response_type, ("".__class__, u"".__class__)):
        response_type = (response_type,)
    for value in response_type:
        client.response_types.add(ResponseType.objects.get(value=value))

    return client


def create_fake_keys():
    '''
    creates a private-public key pair (oidc_provider.models.RSAKey) for use in testing
    '''
    key = RSA.generate(2048)
    return key


def sign_with_key(data, private_key):
    '''
    :param data: a bytes-like object to sign
    :return: the signed message (bytes)
    '''
    # https://pycryptodome.readthedocs.io/en/latest/src/signature/signature.html
    signer = Cryptodome.Signature.pkcs1_15.new(private_key)
    hash = Cryptodome.Hash.SHA384.new()
    hash.update(data)
    return signer.sign(hash)


def create_fake_token(user, scopes, client):
    expires_at = timezone.now() + timezone.timedelta(seconds=60)
    token = Token(user=user, client=client, expires_at=expires_at)
    token.scope = scopes

    token.save()

    return token


def create_fake_dpop_proof(private_key_header=FAKE_RSA4096_PRIVKEY, signing_key=None,
                           htu="https://secureauth.example/token", htm="POST"):
    """
    Constructs a mock DPoP Proof sent by the client.
    """

    #FIXME: PyJWT uses "cryptography" as crypto backend. Extraction and formating should use the same.
    # get the test keypair
    try:
        # build headers from RSA key
        privkey = RSA.import_key(private_key_header)

        # get public params
        modulus = privkey.n
        exponent = privkey.e

        # encode them
        modulus_b64 = to_base64url_uint(modulus).decode()
        exponent_b64 = to_base64url_uint(exponent).decode()

        # build a JWK with RSA-SHA256
        # see: https://www.rfc-editor.org/rfc/rfc7518.html#page-30
        jwk = {
          "kty": "RSA",
          "alg": "RS256",
          "use": "sig",
          "kid": 1,
          "n": modulus_b64,
          "e": exponent_b64
        }

        # may override signkey for tests
        signing_key = RSA.import_key(signing_key) if signing_key else privkey


    except ValueError:
        try:
            # build headers from ECC key
            privkey = ECC.import_key(private_key_header)

            # get public params
            # see: https://github.com/Legrandin/pycryptodome/blob/master/lib/Crypto/Math/_IntegerGMP.py#L171
            x = int(privkey.pointQ.x)
            y = int(privkey.pointQ.y)

            # encode them
            x_b64 = to_base64url_uint(x).decode()
            y_b64 = to_base64url_uint(y).decode()

            # build a JWK with EC-P256-SHA256
            # https://www.rfc-editor.org/rfc/rfc7518.html#page-28
            jwk = {
                "kty": "EC",
                "alg": "ES256",
                "use": "sig",
                "kid": 1,
                "crv": "P-256",
                "x": x_b64,
                "y": y_b64
            }

            # may override signkey for tests
            signing_key = ECC.import_key(signing_key) if signing_key else privkey

        except: raise

    # use the public to check signature with external tools
    #logger.debug(f'PUBKEY: {privkey.publickey().export_key().decode()}')

    # build a DPOP header
    headers = {
      "alg": jwk["alg"],
      "typ": "dpop+jwt",
      "jwk": jwk
    }

    # claim something
    payload = {
        "htu": htu,
        "htm": htm,
        "jti": str(uuid.uuid4()),
        "iat": int(floor(time.time()))
    }

    # build a signed JWT
    return jwt.encode(payload, signing_key.export_key(format="PEM"), algorithm=headers["alg"], headers=headers)


def is_code_valid(url, user, client):
    """
    Check if the code inside the url is valid. Supporting both query string and fragment.
    """
    try:
        parsed = urlsplit(url)
        params = parse_qs(parsed.query or parsed.fragment)
        code = params['code'][0]
        code = Code.objects.get(code=code)
        is_code_ok = (code.client == client) and (code.user == user)
    except Exception:
        is_code_ok = False

    return is_code_ok


def userinfo(claims, user):
    """
    Fake function for setting OIDC_USERINFO.
    """
    claims['given_name'] = 'John'
    claims['family_name'] = 'Doe'
    claims['name'] = '{0} {1}'.format(claims['given_name'], claims['family_name'])
    claims['email'] = user.email
    claims['email_verified'] = True
    claims['address']['country'] = 'Argentina'
    return claims


def fake_sub_generator(user):
    """
    Fake function for setting OIDC_IDTOKEN_SUB_GENERATOR.
    """
    return user.email


def fake_idtoken_processing_hook(id_token, user, **kwargs):
    """
    Fake function for inserting some keys into token. Testing OIDC_IDTOKEN_PROCESSING_HOOK.
    """
    id_token['test_idtoken_processing_hook'] = FAKE_RANDOM_STRING
    id_token['test_idtoken_processing_hook_user_email'] = user.email
    return id_token


def fake_idtoken_processing_hook2(id_token, user, **kwargs):
    """
    Fake function for inserting some keys into token.
    Testing OIDC_IDTOKEN_PROCESSING_HOOK - tuple or list as param
    """
    id_token['test_idtoken_processing_hook2'] = FAKE_RANDOM_STRING
    id_token['test_idtoken_processing_hook_user_email2'] = user.email
    return id_token


def fake_idtoken_processing_hook3(id_token, user, token, **kwargs):
    """
    Fake function for checking scope is passed to processing hook.
    """
    id_token['scope_of_token_passed_to_processing_hook'] = token.scope
    return id_token


def fake_idtoken_processing_hook4(id_token, user, **kwargs):
    """
    Fake function for checking kwargs passed to processing hook.
    """
    id_token['kwargs_passed_to_processing_hook'] = {
        key: repr(value)
        for (key, value) in kwargs.items()
    }
    return id_token


def fake_introspection_processing_hook(response_dict, client, id_token):
    response_dict['test_introspection_processing_hook'] = FAKE_RANDOM_STRING
    return response_dict


class TestAuthBackend:
    def authenticate(self, *args, **kwargs):
        if django.VERSION[0] >= 2 or (django.VERSION[0] == 1 and django.VERSION[1] >= 11):
            assert len(args) > 0 and args[0]
        return ModelBackend().authenticate(*args, **kwargs)
