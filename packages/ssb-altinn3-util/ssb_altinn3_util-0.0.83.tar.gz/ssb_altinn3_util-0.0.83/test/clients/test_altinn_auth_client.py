from pytest_mock.plugin import MockerFixture

from ssb_altinn3_util.clients.auth.altinn_auth_client import AltinnAuthClient
from ssb_altinn3_util.clients.auth.altinn_auth_client import AltinnAuthClientConfig

config = AltinnAuthClientConfig(
    maskinport_client_id="client_id",
    keycloak_secret_path="path_of_secrets",
    platform_environment="unittest",
    altinn_base_url="altinn_url/",
)


def test_get_token(mocker: MockerFixture):
    gcp_auth_mock = mocker.patch("google.auth", autospec=True)
    gcp_auth_mock.default.return_value = "cred", "test_project"
    sm_mock = mocker.patch(
        "ssb_altinn3_util.clients.auth.altinn_auth_client.SecretManagerClient.get_secret",
        return_value="secret",
    )
    kc_mock = mocker.patch(
        "ssb_altinn3_util.clients.auth.altinn_auth_client.KeycloakClient.get_token",
        return_value="keycloak_token",
    )
    mpg_mock = mocker.patch(
        "ssb_altinn3_util.clients.auth.altinn_auth_client.GuardianClient.get_token",
        return_value="maskinport_token",
    )
    ai_mock = mocker.patch(
        "ssb_altinn3_util.clients.auth.altinn_auth_client.AltinnClient.get_altinn_token",
        return_value="faked_token",
    )
    client = AltinnAuthClient(config)

    token = client.get_altinn_auth_token()

    assert token == "faked_token"
    sm_mock.assert_called_once()
    sm_mock.assert_called_with("path_of_secrets")
    kc_mock.assert_called_once()
    kc_mock.assert_called_with(config.maskinport_client_id, "secret")
    mpg_mock.assert_called_once()
    mpg_mock.assert_called_with("keycloak_token")
    ai_mock.assert_called_once()
    ai_mock.assert_called_with("maskinport_token")
