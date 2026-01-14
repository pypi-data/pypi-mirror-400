from pytest_mock.plugin import MockerFixture
import ssb_altinn3_util.clients.altinn.api.application as app_api
from common.mock_response import MockResponse


def test_complete_instance(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b'{"mocked": "schmocked"}'

    mock_request = mocker.patch("requests.post", return_value=mock_response)

    response = app_api.complete_instance(
        token="mocked_token",
        base_url="url/",
        org="org",
        app="app",
        instance_guid="guid",
        instance_owner_party_id=123,
    )

    assert response == '{"mocked": "schmocked"}'
    mock_request.assert_called_once()
    mock_request.assert_called_with(
        "url/org/app/instances/123/guid/complete",
        json="{}",
        headers={"Authorization": "Bearer mocked_token"},
    )
