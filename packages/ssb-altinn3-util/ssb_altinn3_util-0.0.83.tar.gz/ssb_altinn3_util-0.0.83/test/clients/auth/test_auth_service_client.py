import json

from pytest_mock.plugin import MockerFixture
import os
from requests.models import Response


TEST_EMAIL = '{ "email":"user@email.com"}'


def test_auth_service_failed(mocker: MockerFixture):
    mocker.patch.dict(os.environ, {"AUTH_SERVICE_URL": "https://auth.mock"}, clear=True)
    response = Response()
    response.status_code = 418
    response._content = b'{"Something went terribly wrong"}'
    mocker.patch("requests.post", return_value=response)
    from ssb_altinn3_util.security.helpers.auth_service_client import verify_access

    result = verify_access(
        user_email="someone@somewhere.com", requested_role="SOME_ROLE"
    )
    assert result.access_granted == False
    assert result.status_code == 418
    assert result.error_message == '{"Something went terribly wrong"}'


def test_auth_service_ok(mocker: MockerFixture, fake_auth_result_ok):
    mocker.patch.dict(os.environ, {"AUTH_SERVICE_URL": "https://auth.mock"}, clear=True)
    response = Response()
    response.status_code = 200
    response._content = b'{"access_granted":"True","status_code":"200","error_message":"","allowed_forms_read":[],"allowed_forms_write":[]}'
    mocker.patch("requests.post", return_value=response)
    from ssb_altinn3_util.security.helpers.auth_service_client import verify_access

    result = verify_access(
        user_email="someone@somewhere.com", requested_role="SOME_ROLE"
    )
    assert result.access_granted == True
    assert result.status_code == 200
