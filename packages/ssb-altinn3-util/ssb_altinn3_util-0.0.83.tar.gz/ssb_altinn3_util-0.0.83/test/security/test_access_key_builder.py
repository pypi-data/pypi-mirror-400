import pytest
import os
from typing import Optional
from pydantic import BaseModel
from pytest_mock.plugin import MockerFixture
from unittest.mock import Mock
from fastapi import Request, HTTPException

os.environ["NAIS_APP_NAME"] = "test-test"


class AccessTestModel(BaseModel):
    ra_nummer: Optional[str] = None
    skjema_id: Optional[int] = None
    app_id: Optional[str] = None
    periode_id: Optional[int] = None
    periode_aar: Optional[int] = None
    periode_type: Optional[str] = None
    periode_nr: Optional[int] = None
    pulje_id: Optional[int] = None
    utsending_id: Optional[int] = None
    message: str


class MockRequest(Mock):
    state: Mock
    path_params: dict
    query_params: Mock

    def __init__(self, spec, **kwargs):
        super().__init__(spec)
        self.path_params = {}
        self.query_params = Mock()
        setattr(self.query_params, "_dict", {})
        self.state = Mock()
        for k, v in kwargs.items():
            if k == "path_params":
                self.path_params = v
            elif k == "query_params":
                self.query_params._dict = v
            else:
                setattr(self, k, v)


@pytest.mark.parametrize(
    "method,field,val,expected",
    {
        ("POST", "ra_nummer", "RA-1234A3", "RA_NUMMER:RA-1234A3"),
        ("POST", "skjema_id", "42", "SKJEMA_ID:42"),
        ("POST", "app_id", "ra1234-01", "APP_ID:ra1234-01"),
        ("POST", "periode_id", "42", "PERIODE_ID:42"),
        ("POST", "pulje_id", "42", "PULJE_ID:42"),
        ("POST", "utsending_id", "42", "UTSENDING_ID:42"),
        ("POST", None, None, None),
        ("PUT", "ra_nummer", "RA-1234A3", "RA_NUMMER:RA-1234A3"),
        ("PUT", "skjema_id", "42", "SKJEMA_ID:42"),
        ("PUT", "app_id", "ra1234-01", "APP_ID:ra1234-01"),
        ("PUT", "periode_id", "42", "PERIODE_ID:42"),
        ("PUT", "pulje_id", "42", "PULJE_ID:42"),
        ("PUT", "utsending_id", "42", "UTSENDING_ID:42"),
        ("PUT", None, None, None),
    },
)
def test_keybuilder_form_access_post(
    mocker: MockerFixture,
    fake_configparser,
    fake_lab_id_validator,
    fake_auth_header,
    fake_auth_result_ok,
    method,
    field,
    val,
    expected,
):
    fake_lab_id_validator()

    result = fake_auth_result_ok()

    headers = {
        "authorization": fake_auth_header(
            '{"email":"user@ssb.no", "sub":"user", "iss": "https://bob.test"}'
        )
    }

    model = AccessTestModel(message="hello, test")

    if field is not None:
        setattr(model, field, val)
        if field == "periode_aar":
            setattr(model, "periode_type", "KVRT")
            setattr(model, "periode_nr", 1)

    req_mock = MockRequest(
        Request,
        headers=headers,
        method=method,
        _body=model.model_dump_json(exclude_none=True).encode("utf-8"),
    )

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    from ssb_altinn3_util.security.role_authorization import authorize as auth

    @auth(require_role="admin", enable_form_access=True)
    def to_be_authed(required_role, request: Request):
        pass

    if expected is None:
        try:
            to_be_authed("hello", request=req_mock)
            assert False
        except Exception as e:
            auth_call.assert_not_called()
            assert isinstance(e, HTTPException)
            assert e.status_code == 403
    else:
        to_be_authed("hello", request=req_mock)
        auth_call.assert_called_once()
        auth_call.assert_called_with(
            user_email="user@ssb.no",
            requested_role="admin",
            form_access_key=expected,
            is_root_element=False,
        )


@pytest.mark.parametrize(
    "path,field,val,expected",
    {
        ("ra_nummer", "ra_nummer", "RA-1234A3", "RA_NUMMER:RA-1234A3"),
        ("skjema", "skjema_id", "42", "SKJEMA_ID:42"),
        ("app", "app_id", "ra1234-01", "APP_ID:ra1234-01"),
        ("periode", "periode_id", "42", "PERIODE_ID:42"),
        ("pulje", "pulje_id", "42", "PULJE_ID:42"),
        ("utsending", "utsending_id", "42", "UTSENDING_ID:42"),
        ("prefill_meta", "prefill_meta_id", "42", "SKJEMA_PREFILL_META_ID:42"),
        ("utsendingsmal", "utsendingsmal_id", "42", "UTSENDINGSMAL_ID:42"),
    },
)
def test_form_access_delete_key_ok(
    mocker: MockerFixture,
    fake_configparser,
    fake_lab_id_validator,
    fake_auth_result_ok,
    fake_auth_header,
    path: str,
    field: Optional[str],
    val: Optional[str or int],
    expected: Optional[str],
):
    fake_lab_id_validator()
    result = fake_auth_result_ok()
    # mocker.patch.dict(os.environ, {"AUTH_SERVICE_URL": "https://auth.mock"}, clear=True)

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {
        "authorization": fake_auth_header(
            '{"email":"user@ssb.no", "sub":"user", "iss": "https://bob.test"}'
        )
    }

    req_mock = MockRequest(
        Request, headers=headers, method="DELETE", path_params={field: val}
    )

    from ssb_altinn3_util.security.role_authorization import authorize as auth

    @auth(require_role="admin", enable_form_access=True)
    def to_be_authed(required_role, request: Request):
        pass

    to_be_authed("hello", request=req_mock)

    if expected is None:
        auth_call.assert_not_called()
    else:
        auth_call.assert_called_once()
        auth_call.assert_called_with(
            user_email="user@ssb.no",
            requested_role="admin",
            form_access_key=expected,
            is_root_element=False,
        )


##########


@pytest.mark.parametrize(
    "path,field,val,expected",
    {
        ("ra_nummer", "ra_nummer", "RA-1234A3", "RA_NUMMER:RA-1234A3"),
        ("skjema", "skjema_id", "42", "SKJEMA_ID:42"),
    },
)
def test_form_access_query_param_ok(
    mocker: MockerFixture,
    fake_configparser,
    fake_lab_id_validator,
    fake_auth_result_ok,
    fake_auth_header,
    path: str,
    field: Optional[str],
    val: Optional[str or int],
    expected: Optional[str],
):
    fake_lab_id_validator()
    result = fake_auth_result_ok()
    # mocker.patch.dict(os.environ, {"AUTH_SERVICE_URL": "https://auth.mock"}, clear=True)

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {
        "authorization": fake_auth_header(
            '{"email":"user@ssb.no", "sub":"user", "iss": "https://bob.test"}'
        )
    }

    req_mock = MockRequest(
        Request, headers=headers, method="DELETE", query_params={field: val}
    )

    from ssb_altinn3_util.security.role_authorization import authorize as auth

    @auth(require_role="admin", enable_form_access=True)
    def to_be_authed(required_role, request: Request):
        pass

    to_be_authed("hello", request=req_mock)

    if expected is None:
        auth_call.assert_not_called()
    else:
        auth_call.assert_called_once()
        auth_call.assert_called_with(
            user_email="user@ssb.no",
            requested_role="admin",
            form_access_key=expected,
            is_root_element=False,
        )


def test_form_access_post_without_body(
    mocker: MockerFixture,
    fake_configparser,
    fake_lab_id_validator,
    fake_auth_result_ok,
    fake_auth_header,
):
    fake_lab_id_validator()
    result = fake_auth_result_ok()

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {
        "authorization": fake_auth_header(
            '{"email":"user@ssb.no", "sub":"user", "iss": "https://bob.test"}'
        )
    }

    req_mock = MockRequest(
        Request, headers=headers, method="POST", path_params={"app_id": "app-123"}
    )

    from ssb_altinn3_util.security.role_authorization import authorize as auth

    @auth(require_role="admin", enable_form_access=True)
    def to_be_authed(required_role, request: Request):
        pass

    to_be_authed("hello", request=req_mock)

    auth_call.assert_called_with(
        user_email="user@ssb.no",
        requested_role="admin",
        form_access_key="APP_ID:app-123",
        is_root_element=False,
    )
