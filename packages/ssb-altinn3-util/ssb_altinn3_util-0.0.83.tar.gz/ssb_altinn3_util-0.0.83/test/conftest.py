import pytest
from pytest_mock import MockerFixture
import base64
import configparser
from unittest.mock import Mock
from fastapi import Request

from ssb_altinn3_util.security.authorization_result import AuthorizationResult
import ssb_altinn3_util.security.authenticator_constants as constants
from ssb_altinn3_util.security.helpers.token_validators import LabIdValidator


@pytest.fixture(scope="function")
def fake_auth_result_ok():
    def create(include_read_all: bool = False, include_write_all: bool = False):
        read_forms = ["RA1234", "RA9999"]
        write_forms = []
        if include_read_all:
            read_forms = [constants.FORM_ACCESS_ALL]
        if include_write_all:
            write_forms = [constants.FORM_ACCESS_ALL]
        return AuthorizationResult(
            access_granted=True,
            status_code=200,
            allowed_forms_read=read_forms,
            allowed_forms_write=write_forms,
        )

    return create


@pytest.fixture(scope="function")
def fake_auth_result_reject():
    return AuthorizationResult(
        access_granted=False,
        status_code=403,
        error_message="Role requirement not satisfied",
        allowed_forms_read=[],
        allowed_forms_write=[],
    )


@pytest.fixture(scope="function")
def create_fake_request():
    def factory(body: str) -> Request:
        encoded = base64.b64encode(bytes(body.encode("UTF-8"))).decode("UTF-8")

        auth_req: Request = Request(
            scope={
                "type": "http",
                "method": "POST",
                "headers": [
                    (
                        "authorization".encode(),
                        f"Bearer eyAiaGVpIjoiaG9wcCJ9.{encoded}.eyAic2lnIjoic2FnIn0=".encode(),
                    )
                ],
            }
        )

        return auth_req

    return factory


@pytest.fixture(scope="function")
def fake_auth_header():
    def factory(token_payload) -> str:
        encoded = base64.b64encode(bytes(token_payload.encode("UTF-8"))).decode("UTF-8")
        return f"Bearer eyAiaGVpIjoiaG9wcCJ9.{encoded}.eyAic2lnIjoic2FnIn0="

    return factory


@pytest.fixture(scope="function")
def fake_configparser(mocker: MockerFixture):
    class FakeParser(configparser.ConfigParser):
        def read(self, filenames, *args, **kwargs):
            self.read_string(
                "[providers]\nkeys = labId\nenvs = test\n[provider_labId_test]\nauthority = https://bob.test\naudiences = test\ntrusted_issuer = https://bob.test\n"
            )
            return

    mocker.patch("configparser.ConfigParser", side_effect=FakeParser)
    mocker.patch("os.path.exists", return_value=True)


@pytest.fixture(scope="function")
def fake_lab_id_validator(mocker: MockerFixture):
    def configure_mock(email: str = "test@ssb.no"):
        def create_mock(*args, **kwargs):
            fake = Mock()
            fake.get_email_from_token = (
                LabIdValidator.get_email_from_token
            )  # Mock(return_value=email)

            return fake

        mocker.patch(
            "ssb_altinn3_util.security.helpers.token_validators.LabIdValidator",
            side_effect=create_mock,
        )

    return configure_mock
