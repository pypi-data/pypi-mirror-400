import os

from typing import Dict
import base64
import json
import pytest

os.environ["NAIS_APP_NAME"] = "test-test"


@pytest.fixture(scope="function")
def fake_token():
    def create(claims: Dict[str, str]) -> str:
        payload: str = json.dumps(claims)
        return f"Bearer abcd.{base64.b64encode(payload.encode('UTF-8')).decode('UTF-8')}.dcba"

    return create


def test_email_present_ok(fake_token, fake_configparser, fake_lab_id_validator):
    fake_lab_id_validator()
    from ssb_altinn3_util.security.helpers import jwt_helper

    token = fake_token({"sub": "test", "iss": "https://bob.test"})

    email = jwt_helper.get_user_email_from_token(token)

    assert email == "test@ssb.no"


def test_no_email_preferred_user_ok1(
    fake_token, fake_configparser, fake_lab_id_validator
):
    fake_lab_id_validator(email="bob@ssb.no")

    from ssb_altinn3_util.security.helpers import jwt_helper

    token = fake_token(
        {"snailmail": "test@ssb.no", "sub": "bob", "iss": "https://bob.test"}
    )

    email = jwt_helper.get_user_email_from_token(token)

    assert email == "bob@ssb.no"
