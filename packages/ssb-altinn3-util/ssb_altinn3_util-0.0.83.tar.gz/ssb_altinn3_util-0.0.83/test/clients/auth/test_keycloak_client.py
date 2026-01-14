import pytest
from pytest_mock.plugin import MockerFixture

from common.mock_response import MockResponse
from ssb_altinn3_util.clients.auth.helpers.keycloak_client import KeycloakClient


def test_get_token_happy(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b'{"access_token": "kc_token"}'

    mock_request = mocker.patch("requests.post", return_value=mock_response)

    client = KeycloakClient("unittest")
    token = client.get_token("123", "top_secret")

    assert token == "kc_token"
    mock_request.assert_called_once()
    mock_request.assert_called_with(
        "https://keycloak.unittest-bip-app.ssb.no/auth/realms/ssb/protocol/openid-connect/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "maskinporten-123",
            "client_secret": "top_secret",
        },
    )


def test_get_token_exception(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b'{"access_token": "kc_token"}'
    mock_response.status_code = 500

    mock_request = mocker.patch("requests.post", return_value=mock_response)

    client = KeycloakClient("unittest")
    with pytest.raises(Exception) as e:
        client.get_token("123", "top_secret")

    assert str(e.value).startswith(
        "Client 'Keycloak Client' failed to fetch with error:"
    )
    mock_request.assert_called_once()
    mock_request.assert_called_with(
        "https://keycloak.unittest-bip-app.ssb.no/auth/realms/ssb/protocol/openid-connect/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": "maskinporten-123",
            "client_secret": "top_secret",
        },
    )
