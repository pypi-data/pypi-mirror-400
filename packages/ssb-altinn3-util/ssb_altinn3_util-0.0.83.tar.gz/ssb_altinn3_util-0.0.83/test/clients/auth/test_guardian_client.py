import pytest
from pytest_mock.plugin import MockerFixture

from common.mock_response import MockResponse
from ssb_altinn3_util.clients.auth.helpers.guardian_client import GuardianClient


def test_get_token_happy_default_base(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b'{"accessToken": "mp_token"}'

    mock_request = mocker.patch("requests.post", return_value=mock_response)

    client = GuardianClient(base_url="")
    token = client.get_token("top_secret")

    assert token == "mp_token"
    mock_request.assert_called_once()
    mock_request.assert_called_with(
        "http://maskinporten-guardian.dapla.svc.cluster.local/maskinporten/access-token",
        headers={
            "Authorization": "Bearer top_secret",
            "Content-Type": "application/json",
        },
        data="{}",
    )


def test_get_token_exception_default_base(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b'{"accessToken": "mp_token"}'
    mock_response.status_code = 500

    mock_request = mocker.patch("requests.post", return_value=mock_response)

    client = GuardianClient(base_url="")
    with pytest.raises(Exception) as e:
        client.get_token("top_secret")

    assert str(e.value).startswith(
        "Client 'Guardian Client' failed to fetch with error:"
    )
    assert mock_request.call_count == 3
    mock_request.assert_called_with(
        "http://maskinporten-guardian.dapla.svc.cluster.local/maskinporten/access-token",
        headers={
            "Authorization": "Bearer top_secret",
            "Content-Type": "application/json",
        },
        data="{}",
    )


def test_get_token_happy_custom_base(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b'{"accessToken": "mp_token"}'

    mock_request = mocker.patch("requests.post", return_value=mock_response)

    custom_base_url = "http://testurl.com"

    client = GuardianClient(base_url=custom_base_url)
    token = client.get_token("top_secret")

    assert token == "mp_token"
    mock_request.assert_called_once()
    mock_request.assert_called_with(
        f"{custom_base_url}/maskinporten/access-token",
        headers={
            "Authorization": "Bearer top_secret",
            "Content-Type": "application/json",
        },
        data="{}",
    )


def test_get_token_exception_custom_base(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b'{"accessToken": "mp_token"}'
    mock_response.status_code = 500

    mock_request = mocker.patch("requests.post", return_value=mock_response)

    custom_base_url = "http://testurl.com"

    client = GuardianClient(base_url=custom_base_url)
    with pytest.raises(Exception) as e:
        client.get_token("top_secret")

    assert str(e.value).startswith(
        "Client 'Guardian Client' failed to fetch with error:"
    )
    assert mock_request.call_count == 3
    mock_request.assert_called_with(
        f"{custom_base_url}/maskinporten/access-token",
        headers={
            "Authorization": "Bearer top_secret",
            "Content-Type": "application/json",
        },
        data="{}",
    )


def test_get_token_two_tries(mocker: MockerFixture):
    mock_response_bad = MockResponse()
    mock_response_bad.content = b'{"accessToken": "mp_token"}'
    mock_response_bad.status_code = 500

    mock_response_ok = MockResponse()
    mock_response_ok.content = b'{"accessToken": "mp_token"}'

    mock_request = mocker.patch(
        "requests.post", side_effect=[mock_response_bad, mock_response_ok]
    )

    client = GuardianClient(base_url="")

    token = client.get_token("top_secret")

    assert token == "mp_token"
    assert mock_request.call_count == 2
