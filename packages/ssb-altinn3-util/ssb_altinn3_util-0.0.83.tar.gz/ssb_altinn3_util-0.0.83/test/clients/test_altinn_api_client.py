from pytest_mock.plugin import MockerFixture

from ssb_altinn3_util.clients.altinn.altinn_api_client import AltinnApiClient
from ssb_altinn3_util.models.basic_file import BasicFile


def test_client_instantiation(mocker: MockerFixture):
    auth = mocker.patch(
        "ssb_altinn3_util.clients.altinn.altinn_api_client.AltinnAuthClient",
        autospec=True,
    )
    auth.get_altinn_auth_token.return_value = "mocked_token"

    client = AltinnApiClient(
        auth_client=auth,
        altinn_apps_base_url="https://apps.mocked..com",
        altinn_platform_base_url="https://base.mocked.com",
    )

    assert client.auth_client.get_altinn_auth_token() == "mocked_token"


def test_confirm_completed_instance(mocker: MockerFixture):
    auth = mocker.patch(
        "ssb_altinn3_util.clients.altinn.altinn_api_client.AltinnAuthClient",
        autospec=True,
    )
    auth.get_altinn_auth_token.return_value = "mocked_token"
    app_api = mocker.patch(
        "ssb_altinn3_util.clients.altinn.altinn_api_client.application_api.complete_instance",
        return_value="mocked_response",
    )
    client = AltinnApiClient(
        auth_client=auth,
        altinn_apps_base_url="https://apps.mocked.com",
        altinn_platform_base_url="https://base.mocked.com",
    )

    response = client.confirm_completed_instance(
        app="app", org="org", instance_guid="guid", instance_owner_id=123
    )

    assert response == "mocked_response"
    app_api.assert_called_once()
    app_api.assert_called_with(
        token="mocked_token",
        app="app",
        org="org",
        instance_guid="guid",
        instance_owner_party_id=123,
        base_url=client.altinn_apps_base_url,
    )


def test_get_instance(mocker: MockerFixture):
    auth = mocker.patch(
        "ssb_altinn3_util.clients.altinn.altinn_api_client.AltinnAuthClient",
        autospec=True,
    )
    auth.get_altinn_auth_token.return_value = "mocked_token"
    storage_api = mocker.patch(
        "ssb_altinn3_util.clients.altinn.altinn_api_client.storage_api.get_instance",
        return_value="mocked_response",
    )
    client = AltinnApiClient(
        auth_client=auth,
        altinn_apps_base_url="https://apps.mocked.com",
        altinn_platform_base_url="https://base.mocked.com",
    )

    response = client.get_instance(instance_guid="guid", instance_owner_id=123)

    assert response == "mocked_response"
    storage_api.assert_called_once()
    storage_api.assert_called_with(
        token="mocked_token",
        instance_owner_id=123,
        instance_guid="guid",
        platform_base_url=client.altinn_platform_base_url,
    )


def test_get_instance_data_object(mocker: MockerFixture):
    mock_file = BasicFile(
        filename="mock_file.mck",
        content_type="application/mock",
        base64_content="aBcDzYxW1337",
    )
    auth = mocker.patch(
        "ssb_altinn3_util.clients.altinn.altinn_api_client.AltinnAuthClient",
        autospec=True,
    )
    auth.get_altinn_auth_token.return_value = "mocked_token"
    storage_api = mocker.patch(
        "ssb_altinn3_util.clients.altinn.altinn_api_client.storage_api.get_data_for_instance",
        return_value=mock_file,
    )
    client = AltinnApiClient(
        auth_client=auth,
        altinn_apps_base_url="https://apps.mocked.com",
        altinn_platform_base_url="https://base.mocked.com",
    )

    response = client.get_instance_data_object(
        instance_guid="guid", instance_owner_id=123, data_guid="d_guid"
    )

    assert response == mock_file
    storage_api.assert_called_once()
    storage_api.assert_called_with(
        token="mocked_token",
        instance_owner_id=123,
        instance_guid="guid",
        data_guid="d_guid",
        platform_base_url=client.altinn_platform_base_url,
    )


def test_token_cache(mocker: MockerFixture):
    auth = mocker.patch(
        "ssb_altinn3_util.clients.altinn.altinn_api_client.AltinnAuthClient",
        autospec=True,
    )
    auth.get_altinn_auth_token.return_value = "mocked_token"
    app_api = mocker.patch(
        "ssb_altinn3_util.clients.altinn.altinn_api_client.application_api.complete_instance",
        return_value="mocked_response",
    )
    client = AltinnApiClient(
        auth_client=auth,
        altinn_apps_base_url="https://apps.mocked.com",
        altinn_platform_base_url="https://base.mocked.com",
    )

    for _ in range(10):
        response = client.confirm_completed_instance(
            app="app", org="org", instance_guid="guid", instance_owner_id=123
        )

        assert response == "mocked_response"

    assert app_api.call_count == 10
    auth.get_altinn_auth_token.assert_called_once()
