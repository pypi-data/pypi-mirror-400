import pytest
from pydantic import ValidationError

from ssb_altinn3_util.security.post_access_request_models import PostGroupFormAccess


def test_read_access_request_ok():
    request = PostGroupFormAccess(
        group_id=1, form_id=42, access_type="r", user="read_granter@test.com"
    )

    assert request.access_type == "r"


def test_write_access_request_ok():
    request = PostGroupFormAccess(
        group_id=2, form_id=4, access_type="w", user="write_granter@test.com"
    )

    assert request.access_type == "w"


def test_invalid_access_request_error():
    with pytest.raises(ValidationError) as ve:
        PostGroupFormAccess(
            group_id=3, form_id=44, access_type="X", user="error_maker@test.com"
        )

    assert ve.errisinstance(ValidationError)
