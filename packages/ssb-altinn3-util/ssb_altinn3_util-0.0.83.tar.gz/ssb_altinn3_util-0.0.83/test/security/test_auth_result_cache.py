import pytest
import os
from typing import Optional
from pytest_mock.plugin import MockerFixture
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


def get_test_client() -> TestClient:
    from ssb_altinn3_util.security.role_authorization import authorize

    test_app = FastAPI()

    @test_app.get("/cached")
    @authorize(require_role="admin", cache_seconds=100)
    def cached(request: Request) -> str:
        return "hello"

    @test_app.get("/another_cached")
    @authorize(require_role="admin", cache_seconds=100)
    def cached_nr_2(request: Request) -> str:
        return "hello"

    @test_app.get("/not_cached")
    @authorize(require_role="admin")
    def not_cached(request: Request) -> str:
        return "hello"

    return TestClient(test_app)


def test_non_cached_called_once(
    mocker: MockerFixture,
    fake_auth_result_ok,
    fake_auth_header,
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

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {
        "authorization": fake_auth_header(
            '{"email":"user@ssb.no", "sub": "user", "iss":"https://bob.test"}'
        )
    }

    client = get_test_client()
    response = client.get("/not_cached", headers=headers)

    assert response.json() == "hello"
    auth_call.assert_called_once()
    auth_call.assert_called_with(
        user_email="user@ssb.no",
        requested_role="admin",
        form_access_key=None,
        is_root_element=False,
    )


def test_non_cached_called_twice(
    mocker: MockerFixture,
    fake_auth_result_ok,
    fake_auth_header,
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

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {
        "authorization": fake_auth_header(
            '{"email":"user@ssb.no", "sub": "user", "iss":"https://bob.test"}'
        )
    }
    client = get_test_client()
    response = client.get("/not_cached", headers=headers)
    response2 = client.get("/not_cached", headers=headers)

    assert response.json() == "hello"
    assert response2.json() == "hello"
    assert auth_call.call_count == 2
    auth_call.assert_called_with(
        user_email="user@ssb.no",
        requested_role="admin",
        form_access_key=None,
        is_root_element=False,
    )


def test_cached_called_once(
    mocker: MockerFixture, fake_auth_result_ok, fake_auth_header
):
    result = fake_auth_result_ok()
    mocker.patch.dict(
        os.environ,
        {"AUTH_SERVICE_URL": "https://auth.mock", "NAIS_APP_NAME": "test-test"},
        clear=True,
    )

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {
        "authorization": fake_auth_header(
            '{"email":"user@ssb.no", "sub": "user", "iss":"https://bob.test"}'
        )
    }
    client = get_test_client()
    response = client.get("/cached", headers=headers)

    assert response.json() == "hello"
    auth_call.assert_called_once()
    auth_call.assert_called_with(
        user_email="user@ssb.no",
        requested_role="admin",
        form_access_key=None,
        is_root_element=False,
    )


def test_cached_called_twice(
    mocker: MockerFixture, fake_auth_result_ok, fake_auth_header
):
    result = fake_auth_result_ok()
    mocker.patch.dict(
        os.environ,
        {"AUTH_SERVICE_URL": "https://auth.mock", "NAIS_APP_NAME": "test-test"},
        clear=True,
    )

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {
        "authorization": fake_auth_header(
            '{"email":"user@ssb.no", "sub": "user", "iss":"https://bob.test"}'
        )
    }
    client = get_test_client()
    response = client.get("/cached", headers=headers)
    response2 = client.get("/cached", headers=headers)

    assert response.json() == "hello"
    assert response2.json() == "hello"
    auth_call.assert_called_once()
    auth_call.assert_called_with(
        user_email="user@ssb.no",
        requested_role="admin",
        form_access_key=None,
        is_root_element=False,
    )


def test_cached_cache_distinct_per_endpoint(
    mocker: MockerFixture, fake_auth_result_ok, fake_auth_header
):
    result = fake_auth_result_ok()
    mocker.patch.dict(
        os.environ,
        {"AUTH_SERVICE_URL": "https://auth.mock", "NAIS_APP_NAME": "test-test"},
        clear=True,
    )

    auth_call = mocker.patch(
        "ssb_altinn3_util.security.helpers.auth_service_client.verify_access",
        return_value=result,
    )

    headers = {
        "authorization": fake_auth_header(
            '{"email":"user@ssb.no", "sub": "user", "iss":"https://bob.test"}'
        )
    }
    client = get_test_client()
    response = client.get("/cached", headers=headers)
    _ = client.get("/cached", headers=headers)
    response2 = client.get("/another_cached", headers=headers)
    _ = client.get("/another_cached", headers=headers)

    assert response.json() == "hello"
    assert response2.json() == "hello"
    assert auth_call.call_count == 2
    auth_call.assert_called_with(
        user_email="user@ssb.no",
        requested_role="admin",
        form_access_key=None,
        is_root_element=False,
    )
