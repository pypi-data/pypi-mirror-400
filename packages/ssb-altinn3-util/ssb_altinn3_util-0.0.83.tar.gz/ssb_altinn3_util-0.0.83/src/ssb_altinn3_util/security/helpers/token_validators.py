import json
import base64
import requests
from fastapi import HTTPException
import logging

from jwt import PyJWKClient
import jwt


logger = logging.getLogger()


class ValidatorConfig:
    authority_url: str
    issuer: str
    audiences: list[str]

    def __init__(self, authority: str, issuer: str, audiences: str):
        self.authority_url = authority
        self.issuer = issuer
        self.audiences = audiences.split(",")


class BaseTokenValidator:
    def validate_token(self, token: str) -> str:
        pass

    @staticmethod
    def get_email_from_token(token: str) -> str:
        pass


class AuthSSBValidator(BaseTokenValidator):
    client: PyJWKClient
    config: ValidatorConfig

    def __init__(self, config: ValidatorConfig):
        self.client = PyJWKClient(
            uri=f"{config.authority_url}/protocol/openid-connect/certs"
        )
        self.config = config

    def validate_token(self, token: str) -> str:
        try:
            signing_key = self.client.get_signing_key_from_jwt(token=token)

            _ = jwt.decode(
                jwt=token,
                key=signing_key.key,
                algorithms=["RS256"],
                audience=self.config.audiences,
                issuer=self.config.issuer,
                options={"verify_exp": True},
            )
            return self.get_user_email_from_token(token)
        except Exception as e:
            raise HTTPException(
                status_code=401, detail=f"Failed to authenticate user with error: {e}"
            )

    @staticmethod
    def get_user_email_from_token(token: str) -> str:
        """Get the user email from the jwt token"""
        token_json = _get_token_payload_json(token=token)

        email: str = token_json.get("email")

        if not email:
            preferred_username: str = token_json.get("preferred_username")

            if not preferred_username:
                return ""

            email = (
                preferred_username
                if preferred_username.endswith("@ssb.no")
                else f"{preferred_username}@ssb.no"
            )

        return email


class LabIdValidator(BaseTokenValidator):
    client: PyJWKClient
    config: ValidatorConfig

    def __init__(self, config: ValidatorConfig):
        url = f"{config.authority_url}/.well-known/openid-configuration"
        try:
            result = requests.get(url=url)

            oidc_config = result.json()

            headers = {"User-agent": "suv-test-auth"}

            self.client = PyJWKClient(oidc_config["jwks_uri"], headers=headers)
            self.config = config
        except Exception as e:
            logger.error(f"Failed to setup LabId-validator due to error: {e}")
            raise

    def validate_token(self, token: str) -> str:
        try:
            signing_key = self.client.get_signing_key_from_jwt(token=token)

            _ = jwt.decode(
                jwt=token,
                key=signing_key.key,
                algorithms=["RS256"],
                audience=self.config.audiences,
                issuer=self.config.issuer,
                options={"verify_exp": True},
            )

            return self.get_email_from_token(token)
        except Exception as e:
            raise HTTPException(
                status_code=401, detail=f"Failed to authenticate user with error: {e}"
            )

    @staticmethod
    def get_email_from_token(token: str) -> str:
        token_json = _get_token_payload_json(token=token)

        subject = token_json.get("sub")

        if not subject:
            return ""

        return f"{subject}@ssb.no"


def _get_token_payload_json(token: str) -> dict:
    payload = token.split(sep=".")[1]
    token_decoded = base64.b64decode(payload + "==").decode("UTF-8")
    token_json: dict = json.loads(token_decoded)
    return token_json
