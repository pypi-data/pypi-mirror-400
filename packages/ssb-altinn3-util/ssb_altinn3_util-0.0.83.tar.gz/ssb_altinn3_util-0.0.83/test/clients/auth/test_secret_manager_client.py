from pytest_mock import MockFixture

from ssb_altinn3_util.clients.auth.helpers.secret_manager_client import (
    SecretManagerClient,
)


class MockPayload:
    data: bytes


class MockSecret:
    payload: MockPayload


def test_get_secret_ok(mocker: MockFixture):
    mock_secret = MockSecret()
    mock_payload = MockPayload()
    mock_payload.data = b"secret"
    mock_secret.payload = mock_payload

    gcp_auth = mocker.patch("google.auth", autospec=True)
    gcp_auth.default.return_value = "creds", "project"
    mock_secretmanager_client = mocker.patch(
        "google.cloud.secretmanager.SecretManagerServiceClient", autospec=True
    )
    mock_secretmanager_client.return_value.access_secret_version.return_value = (
        mock_secret
    )

    client = SecretManagerClient()

    secret = client.get_secret("path")

    assert secret == "secret"
    mock_secretmanager_client.assert_called_once()
