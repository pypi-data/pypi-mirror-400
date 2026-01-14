import pytest
from pytest_mock.plugin import MockerFixture

from common.mock_response import MockResponse
from ssb_altinn3_util.clients.auth.helpers.altinn_client import AltinnClient


def test_get_token_happy(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b"altinn_token"

    mock_request = mocker.patch("requests.get", return_value=mock_response)

    client = AltinnClient("url/")
    token = client.get_altinn_token("mp_token")

    assert token == "altinn_token"
    mock_request.assert_called_once()
    mock_request.assert_called_with(
        "url/authentication/api/v1/exchange/maskinporten?test=true",
        headers={"Authorization": "Bearer mp_token"},
    )


def test_get_token_exception(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b"This should not be returned"
    mock_response.status_code = 500

    mock_request = mocker.patch("requests.get", return_value=mock_response)

    client = AltinnClient("url/")
    with pytest.raises(Exception) as e:
        client.get_altinn_token("mp_token")

    assert str(e.value).startswith("Client 'Altinn Client' failed to fetch with error:")
    mock_request.assert_called_once()
    mock_request.assert_called_with(
        "url/authentication/api/v1/exchange/maskinporten?test=true",
        headers={"Authorization": "Bearer mp_token"},
    )
