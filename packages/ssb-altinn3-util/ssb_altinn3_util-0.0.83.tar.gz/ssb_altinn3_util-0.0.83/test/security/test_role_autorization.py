import os

import pytest
from fastapi import Request, HTTPException
from pytest_mock.plugin import MockerFixture

import ssb_altinn3_util.security.authenticator_constants as constants

# from ssb_altinn3_util.security.role_authorization import authorize


TEST_PAYLOAD = '{ "email":"user@ssb.no", "sub":"user", "iss":"https://bob.test"}'


def test_authorize_ok_1(
    mocker: MockerFixture,
    fake_auth_result_ok,
    create_fake_request,
    fake_configparser,
    fake_lab_id_validator,
):
    fake_lab_id_validator()
    result = fake_auth_result_ok()
    mocker.patch.dict(
        os.environ,
        {"AUTH_SERVICE_URL": "https://auth.mock", "NAIS_APP_NAME": "test-test"},
        clear=True,
    )

    auth_client_mock = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    auth_req: Request = create_fake_request(TEST_PAYLOAD)

    visited = False

    from ssb_altinn3_util.security.role_authorization import authorize

    @authorize(require_role=constants.ROLE_ADMIN)
    def verify_method_ok(request: Request):
        nonlocal visited
        visited = True

    verify_method_ok(request=auth_req)

    assert visited
    auth_client_mock.assert_called_once()

    visited = False

    verify_method_ok(auth_req)

    assert visited
    assert auth_client_mock.call_count == 2


def test_no_token_401(mocker: MockerFixture, fake_configparser, fake_lab_id_validator):
    fake_lab_id_validator()

    mocker.patch.dict(
        os.environ,
        {"AUTH_SERVICE_URL": "https://auth.mock", "NAIS_APP_NAME": "test-test"},
        clear=True,
    )

    with pytest.raises(HTTPException) as he:
        auth_req: Request = Request(
            scope={
                "type": "http",
                "headers": [
                    (
                        "banana".encode(),
                        "Bearer eyAiaGVpIjoiaG9wcCJ9.eyAiZW1haWwiOiJ1c2VyQGVtYWlsLmNvbSJ9.eyAic2lnIjoic2FnIn0=".encode(),
                    )
                ],
            }
        )

        from ssb_altinn3_util.security.role_authorization import authorize

        @authorize(require_role=constants.ROLE_ADMIN)
        def test_auth(request: Request):
            pass

        test_auth(auth_req)

    assert he.value.status_code == 401
    assert he.value.detail == "Authorization header missing"


def test_cant_get_email_from_token_401(
    mocker: MockerFixture,
    fake_configparser,
    fake_lab_id_validator,
    create_fake_request,
    fake_auth_result_reject,
):
    fake_lab_id_validator()
    mocker.patch.dict(
        os.environ,
        {"AUTH_SERVICE_URL": "https://auth.mock", "NAIS_APP_NAME": "test-test"},
        clear=True,
    )

    mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=fake_auth_result_reject,
    )

    with pytest.raises(HTTPException) as he:
        auth_req: Request = create_fake_request(
            '{"snailmail":"yep", "iss": "https://bob.test"}'
        )

        from ssb_altinn3_util.security.role_authorization import authorize

        @authorize(require_role=constants.ROLE_ADMIN)
        def test_auth(request: Request):
            pass

        test_auth(auth_req)

    assert he.value.status_code == 401
    assert he.value.detail == "Unable to find user email in supplied token!"


def test_request_rejected_403(
    mocker: MockerFixture,
    fake_auth_result_reject,
    create_fake_request,
    fake_configparser,
    fake_lab_id_validator,
):
    fake_lab_id_validator()
    mocker.patch.dict(
        os.environ,
        {"AUTH_SERVICE_URL": "https://auth.mock", "NAIS_APP_NAME": "test-test"},
        clear=True,
    )

    mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=fake_auth_result_reject,
    )

    with pytest.raises(HTTPException) as he:
        auth_req: Request = create_fake_request(TEST_PAYLOAD)

        from ssb_altinn3_util.security.role_authorization import authorize

        @authorize(require_role=constants.ROLE_ADMIN)
        def test_auth(request: Request):
            pass

        test_auth(auth_req)

    assert he.value.status_code == 403
    assert he.value.detail == "Role requirement not satisfied"


def test_authenticator_multirole_ok_1(
    mocker: MockerFixture,
    fake_auth_result_ok,
    create_fake_request,
    fake_configparser,
    fake_lab_id_validator,
):
    fake_lab_id_validator()
    result = fake_auth_result_ok()
    mocker.patch.dict(
        os.environ,
        {"AUTH_SERVICE_URL": "https://auth.mock", "NAIS_APP_NAME": "test-test"},
        clear=True,
    )

    auth_client_mock = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    auth_req: Request = create_fake_request(TEST_PAYLOAD)

    visited = False

    from ssb_altinn3_util.security.role_authorization import authorize

    @authorize(require_role=f"{constants.ROLE_SUPERUSER},{constants.ROLE_FORM_WRITER}")
    def test_auth(request: Request):
        nonlocal visited
        visited = True

    test_auth(auth_req)

    auth_client_mock.assert_called_once()
    assert visited


def test_authenticator_multirole_user_has_one_role(
    mocker: MockerFixture,
    fake_auth_result_ok,
    fake_auth_result_reject,
    create_fake_request,
    fake_configparser,
    fake_lab_id_validator,
):
    fake_lab_id_validator()
    mocker.patch.dict(
        os.environ,
        {"AUTH_SERVICE_URL": "https://auth.mock", "NAIS_APP_NAME": "test-test"},
        clear=True,
    )

    auth_client_mock = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        side_effect=[fake_auth_result_reject, fake_auth_result_ok()],
    )

    auth_req: Request = create_fake_request(TEST_PAYLOAD)

    visited = False

    from ssb_altinn3_util.security.role_authorization import authorize

    @authorize(require_role=f"{constants.ROLE_SUPERUSER},{constants.ROLE_FORM_WRITER}")
    def test_auth(request: Request):
        nonlocal visited
        visited = True

    test_auth(auth_req)

    assert auth_client_mock.call_count == 2
    assert visited
