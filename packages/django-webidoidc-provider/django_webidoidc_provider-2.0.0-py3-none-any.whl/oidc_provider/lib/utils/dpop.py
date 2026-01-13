import json
import logging
from Cryptodome.PublicKey import (RSA, ECC)
from Cryptodome.Hash import SHA256
from oidc_provider.lib.errors import (
    TokenError,
)
import jwt
from jwt.utils import (from_base64url_uint, base64url_decode, base64url_encode)
from jwt.exceptions import *
from django.conf import settings

logger = logging.getLogger(__name__)


def construct_key(jwk):
    # extract ECC key
    if jwk['kty'] == 'EC' and jwk['alg'] == 'ES256':
        logger.debug('Loading ECC key...')

        # decode public params
        x = from_base64url_uint(jwk['x'])
        y = from_base64url_uint(jwk['y'])

        # build the public key
        return ECC.construct(curve=jwk['crv'], point_x=x, point_y=y)

    # extract RSA key
    elif jwk['kty'] == 'RSA' and jwk['alg'] == 'RS256':
        logger.debug('Loading RSA key...')

        # decode public params
        modulus = from_base64url_uint(jwk['n'])
        exponent = from_base64url_uint(jwk['e'])

        # build the public key
        return RSA.construct((modulus, exponent))

    else:
        raise TokenError('algorithm not implemented!')


def verify_signature(jwk, dpop_proof, audience=None):
    try:
        pub_key = construct_key(jwk)
        jwt.decode(dpop_proof, key=pub_key.export_key(format='PEM'), algorithms=["ES256", "RS256"], audience=audience, leeway=getattr(settings, 'OIDC_DPOP_LEEWAY', 1))
    except InvalidAudienceError as e:
        logger.error(f'Audience isn\'t right: {str(e)}')
        raise TokenError('Invalid audience.')


def verify_dpop_proof(dpop_proof):
    """
    DPoP - Verifies the signed JWT after extracting the public key from the header
    :raises: TokenError if DPoP proof invalid
    :return: the decoded DPoP proof JWK
    """
    try:
        # will arrive in three segments
        headers = dpop_proof.split('.')[0]

        # get the jwk
        jwk = json.loads(base64url_decode(headers))['jwk']

        # verify DPOP proof signature
        verify_signature(jwk, dpop_proof)

    except KeyError:
        logger.error('Wrong format. JWK is not present or doesn\'t have the required parameters')
        raise TokenError('DPOP malformated.')

    except DecodeError:
        logger.error('Wrong format. DPOP proof encoding is not valid')
        raise TokenError('DPOP wrong encoding.')

    except (InvalidTokenError, InvalidSignatureError, ExpiredSignatureError, InvalidAlgorithmError,
            InvalidIssuerError, InvalidIssuedAtError, ImmatureSignatureError, InvalidKeyError) as e:
        logger.error(f'Wrong signature. {str(e)}')
        raise TokenError('Signature validation error')

    except MissingRequiredClaimError as e:
        logger.error(f'Missing claim: {str(e)}')
        raise TokenError('Missing claim.')

    except InvalidAudienceError as e:
        logger.error(f'Audience isn\'t right: {str(e)}')
        raise TokenError('Invalid audience.')

    return jwk


def verify_thumbprint(jwk, thumbprint):
    """
    verifies that the passed public key corresponds to the passed thumbprint
    :raises: TokenError if the thumbrpint does not match
    """
    other_thumbprint = compute_thumbprint(jwk)
    if thumbprint != other_thumbprint:
        raise TokenError('thumbprint_not_matching_dpop_token')


def compute_thumbprint(jwk):
    """Get a JSON Web Key and compute a thumbprint according to RFC 7638."""
    # see: https://tools.ietf.org/html/rfc7638
    try:
        # keep only required params in lexicographic order
        if jwk['alg'] == 'RS256':
            params = {key: jwk[key] for key in ['e', 'kty', 'n']}
        elif jwk['alg'] == 'ES256':
            params = {key: jwk[key] for key in ['crv', 'kty', 'x', 'y']}
        else:
            raise TokenError('algorithm not implemented!')

        # order them into a json string
        params = json.dumps(params, sort_keys=True, separators=(',', ':')).encode('utf-8')

        # hash
        h = SHA256.new()
        h.update(params)

        # encode
        thumbprint = base64url_encode(h.digest())

        return thumbprint.decode()

    except PyJWKError as e:
        logger.error(f'error calculating the thumbprint: {e}')
        raise TokenError('invalid thumbprint')
