import pytest
from pytest_mock.plugin import MockerFixture

import ssb_altinn3_util.clients.altinn.api.storage as storage_api
from ssb_altinn3_util.models.basic_file import BasicFile
from common.mock_response import MockResponse


def test_get_instance(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b'{"mocked": "mocked"}'
    mock_request = mocker.patch("requests.get", return_value=mock_response)
    response = storage_api.get_instance(
        token="mocked_token",
        instance_guid="guid",
        instance_owner_id=123,
        platform_base_url="url/",
    )

    assert response == '{"mocked": "mocked"}'
    mock_request.assert_called_once()
    mock_request.assert_called_with(
        "url/storage/api/v1/instances/123/guid",
        headers={"Authorization": "Bearer mocked_token"},
    )


def test_get_data_for_instance(mocker: MockerFixture):
    mock_response = MockResponse()
    mock_response.content = b"Gummybear"
    mock_response.headers = {
        "Content-Disposition": "filename=mockfile.mck;",
        "Content-Type": "application/mock",
    }
    mock_request = mocker.patch("requests.get", return_value=mock_response)

    response = storage_api.get_data_for_instance(
        token="mocked_token",
        instance_owner_id=123,
        instance_guid="i_guid",
        data_guid="d_guid",
        platform_base_url="url/",
    )

    assert isinstance(response, BasicFile)
    assert response.filename == "mockfile.mck"
    assert response.content_type == "application/mock"
    assert response.base64_content == "R3VtbXliZWFy"
    mock_request.assert_called_once()
    mock_request.assert_called_with(
        "url/storage/api/v1/instances/123/i_guid/data/d_guid",
        headers={"Authorization": "Bearer mocked_token"},
    )


@pytest.mark.parametrize(
    "content_dispostion_string,expected",
    [
        (
            "stuff=morestuff; filename=testfile1.txt; morestuff=evenmorestuff; buff=knuff;",
            "testfile1.txt",
        ),
        (
            "filename=testfile2.txt; stuff=morestuff; morestuff=evenmorestuff",
            "testfile2.txt",
        ),
        (
            'stuff=morestuff; filename="testfile3.txt"; morestuff=evenmorestuff',
            "testfile3.txt",
        ),
        ("", None),
    ],
)
def test__get_filename_from_headers(content_dispostion_string: str, expected: str):
    headers = {"thing": "object", "Content-Type": "undefined/test"}
    if content_dispostion_string:
        headers["Content-Disposition"] = content_dispostion_string
    filename = storage_api._get_filename_from_headers(headers)
    assert filename == expected
