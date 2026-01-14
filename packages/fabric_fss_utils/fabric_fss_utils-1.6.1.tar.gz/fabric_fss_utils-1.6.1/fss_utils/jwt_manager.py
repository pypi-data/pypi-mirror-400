#!/usr/bin/env python3
import base64
import enum
import gzip
import traceback
import json
from datetime import timedelta, datetime
from typing import Tuple, Union

import jwt
from authlib.jose.rfc7517 import JsonWebKey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


@enum.unique
class ValidateCode(enum.Enum):
    VALID = 1
    UNSPECIFIED_KEY = 2
    UNSPECIFIED_ALG = 3
    UNKNOWN_KEY = 4
    INVALID = 5
    UNABLE_TO_FETCH_KEYS = 6
    UNPARSABLE_TOKEN = 7
    UNABLE_TO_DECODE_KEYS = 8
    UNABLE_TO_LOAD_KEYS = 9
    UNABLE_TO_COMPRESS = 10
    UNABLE_TO_DECOMPRESS = 11
    UNSPECIFIED_ID_TOKEN = 12

    def interpret(self, exception=None):
        interpretations = {
            1: "Token is valid",
            2: "Token does not specify key ID",
            3: "Token does not specify algorithm",
            4: "Unable to find public key at JWK endpoint",
            5: "Token signature is invalid",
            6: "Unable to fetch keys from the endpoint",
            7: "Unable to parse token",
            8: "Unable to decode public keys",
            9: "Unable to load key from file",
            10: "Unable to compress the encoded token",
            11: "Unable to decompress the encoded token",
            12: "Identity Token or Identity Claims not specified"
        }
        if exception is None:
            return interpretations[self.value]
        else:
            return f"{str(exception)}. {interpretations[self.value]}"


class JWTManager:
    @staticmethod
    def _add_padding(data: Union[str, bytes]) -> str:
        """
        Ensures base64 string length is a multiple of 4 by adding '=' padding.
        """
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        rem = len(data) % 4
        if rem > 0:
            data += "=" * (4 - rem)
        return data

    @staticmethod
    def decode_jwt_payload(*, token: str) -> Tuple[ValidateCode, Union[Exception, dict]]:
        """
        Decode the payload section of a JWT token without verification.
        """
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return ValidateCode.UNPARSABLE_TOKEN, Exception("JWT must have 3 parts")

            # Extract and pad payload (index 1)
            payload_padded = JWTManager._add_padding(parts[1])
            payload_bytes = base64.urlsafe_b64decode(payload_padded)
            return ValidateCode.VALID, json.loads(payload_bytes.decode('utf-8'))
        except Exception as e:
            return ValidateCode.UNPARSABLE_TOKEN, e

    @staticmethod
    def encode_and_sign_with_private_key(*, validity: int, claims: dict, private_key_file_name: str, kid: str,
                                         algorithm: str,
                                         pass_phrase: str = None) -> Tuple[ValidateCode, Union[Exception, str]]:
        if pass_phrase:
            pass_phrase = pass_phrase.encode("utf-8")
        else:
            pass_phrase = None

        try:
            with open(private_key_file_name, 'rb') as private_key_fh:
                pem_data = private_key_fh.read()
                private_key = serialization.load_pem_private_key(data=pem_data,
                                                                 password=pass_phrase,
                                                                 backend=default_backend())
        except Exception as e:
            return ValidateCode.UNABLE_TO_LOAD_KEYS, e

        now = datetime.now()
        claims['iat'] = int(now.timestamp())
        claims['exp'] = int((now + timedelta(seconds=int(validity))).timestamp())

        try:
            # PyJWT returns a string in modern versions, but we ensure it's handled
            encoded_token = jwt.encode(claims, private_key, algorithm=algorithm, headers={'kid': kid})
            return ValidateCode.VALID, encoded_token
        except Exception as e:
            return ValidateCode.INVALID, e

    @staticmethod
    def encode_jwk(*, key_file_name: str, kid: str, alg: str) -> Tuple[ValidateCode, Union[Exception, dict]]:
        try:
            with open(key_file_name, 'r') as public_key_fh:
                pem_data = public_key_fh.read()
        except Exception as e:
            return ValidateCode.UNABLE_TO_LOAD_KEYS, e

        try:
            result = dict(JsonWebKey.import_key(pem_data, options={'kty': 'RSA'}))
            result.update({"kid": kid, "alg": alg, "use": "sig"})
            return ValidateCode.VALID, result
        except Exception as e:
            return ValidateCode.INVALID, e

    @staticmethod
    def encode_and_compress(*, claims: dict, secret: str, validity: int, algorithm: str = 'HS256',
                            compression: bool = True) -> Tuple[ValidateCode, Union[Exception, str]]:
        if validity is not None:
            claims['exp'] = int((datetime.now() + timedelta(seconds=int(validity))).timestamp())

        try:
            encoded_jwt = jwt.encode(claims, secret, algorithm=algorithm)

            if compression:
                compressed = gzip.compress(bytes(encoded_jwt, 'utf-8'))
                # b64encode includes padding by default, but we'll be explicit
                encoded_b64 = base64.urlsafe_b64encode(compressed).decode('utf-8')
                return ValidateCode.VALID, encoded_b64

            return ValidateCode.VALID, encoded_jwt
        except Exception as e:
            return ValidateCode.INVALID, e

    @staticmethod
    def decode(*, cookie: str, secret: str = '', verify: bool = True,
               compression: bool = False) -> Tuple[ValidateCode, Union[Exception, dict]]:
        try:
            if compression:
                # Strictly add padding before decoding the custom envelope
                padded_cookie = JWTManager._add_padding(cookie)
                decoded_64 = base64.urlsafe_b64decode(padded_cookie)
                cookie = gzip.decompress(decoded_64)
        except Exception as e:
            traceback.print_exc()
            return ValidateCode.UNABLE_TO_DECOMPRESS, e

        try:
            # Note: PyJWT's decode handles the internal JWT part padding itself
            header = jwt.get_unverified_header(cookie)
            algorithm = header.get('alg')
            if not algorithm:
                return ValidateCode.UNSPECIFIED_ALG, None

            decoded_token = jwt.decode(cookie, secret, algorithms=[algorithm], options={'verify_signature': verify})
            return ValidateCode.VALID, decoded_token
        except jwt.DecodeError as e:
            traceback.print_exc()
            return ValidateCode.UNPARSABLE_TOKEN, e
        except Exception as e:
            traceback.print_exc()
            return ValidateCode.INVALID, e
