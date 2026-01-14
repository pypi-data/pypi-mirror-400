import base64
import json
from typing import Dict

from fastapi import HTTPException

from ssb_altinn3_util.security.auth_handler import AuthHandler
from ssb_altinn3_util.security.helpers.token_validators import BaseTokenValidator


auth_handler = AuthHandler.get_instance()


def validate_token(token: str) -> str:
    issuer = _get_issuer_from_token(token)

    validator = _get_validator(issuer=issuer)

    return validator.validate_token(token=token)


def get_user_email_from_token(token: str) -> str:
    issuer = _get_issuer_from_token(token=token)
    validator = _get_validator(issuer=issuer)
    return validator.get_email_from_token(token=token)


def _get_issuer_from_token(token: str) -> str:
    payload = token.split(".")[1]
    token_decoded = base64.b64decode(payload + "==").decode("UTF-8")
    token_json: Dict = json.loads(token_decoded)
    return token_json["iss"]


def _get_validator(issuer: str) -> BaseTokenValidator:
    validator = auth_handler.get_validator(issuer)

    if validator is None:
        raise HTTPException(
            status_code=401, detail=f"Unsupported token issuer '{issuer}'"
        )

    return validator
