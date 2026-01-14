import os

import pytest
from pydantic import ValidationError
from pytest_mock.plugin import MockerFixture

from ssb_altinn3_util.models.altinn3_cloud_event import Altinn3CloudEvent


def test_create_event_valid_source(mocker: MockerFixture):
    mocker.patch.dict(
        os.environ, {"APPROVED_EVENT_SOURCE_URL": "https://approved.mock"}, clear=True
    )
    Altinn3CloudEvent(
        alternativesubject="altsubject",
        data="",
        datacontenttype="datatype",
        id="123",
        source="https://approved.mock",
        specversion="1.2.3",
        subject="testorg",
        time="littførlunsj",
        type="test",
        resource="urn:altinn:resource:app_ssb_skjema",
        resourceinstance="party/instans-uuid",
    )
    assert True


def test_create_event_invalid_source(mocker: MockerFixture):
    mocker.patch.dict(
        os.environ, {"APPROVED_EVENT_SOURCE_URL": "https://approved.mock"}, clear=True
    )
    with pytest.raises(ValueError) as e:
        Altinn3CloudEvent(
            alternativesubject="altsubject",
            data="",
            datacontenttype="datatype",
            id="123",
            source="https://unsafe.mock",
            specversion="1.2.3",
            subject="testorg",
            time="littførlunsj",
            type="test",
            resource="urn:altinn:resource:app_ssb_skjema",
            resourceinstance="party/instans-uuid",
        )

    assert (
        "Provided event source 'https://unsafe.mock' did not match expected source 'https://approved.mock'"
        in str(e.value)
    )
    assert e.type == ValidationError


def test_create_event_env_not_set(mocker: MockerFixture):
    mocker.patch.dict(os.environ, {}, clear=True)
    with pytest.raises(ValueError) as e:
        Altinn3CloudEvent(
            alternativesubject="altsubject",
            data="",
            datacontenttype="datatype",
            id="123",
            source="https://unsafe.mock",
            specversion="1.2.3",
            subject="testorg",
            time="littførlunsj",
            type="test",
            resource="urn:altinn:resource:app_ssb_skjema",
            resourceinstance="party/instans-uuid",
        )

    assert "Environment variable 'APPROVED_EVENT_SOURCE_URL' not found!" in str(e.value)
    assert e.type == ValidationError


def test_create_validate_event_no_time_ok(mocker: MockerFixture):
    mocker.patch.dict(
        os.environ, {"APPROVED_EVENT_SOURCE_URL": "https://approved.mock"}, clear=True
    )
    Altinn3CloudEvent(
        alternativesubject="altsubject",
        data="",
        datacontenttype="datatype",
        id="123",
        source="https://approved.mock",
        specversion="1.2.3",
        subject="testorg",
        type="platform.events.validatesubscription",
        resource="urn:altinn:resource:app_ssb_skjema",
        resourceinstance="party/instans-uuid",
    )
    assert True


def test_create_validate_event_no_subject_ok(mocker: MockerFixture):
    mocker.patch.dict(
        os.environ, {"APPROVED_EVENT_SOURCE_URL": "https://approved.mock"}, clear=True
    )
    Altinn3CloudEvent(
        alternativesubject="altsubject",
        data="",
        datacontenttype="datatype",
        id="123",
        source="https://approved.mock",
        specversion="1.2.3",
        time="littførlunsj",
        type="platform.events.validatesubscription",
        resource="urn:altinn:resource:app_ssb_skjema",
        resourceinstance="party/instans-uuid",
    )
    assert True


def test_create_instance_event_no_time_error(mocker: MockerFixture):
    mocker.patch.dict(
        os.environ, {"APPROVED_EVENT_SOURCE_URL": "https://approved.mock"}, clear=True
    )
    with pytest.raises(ValueError) as e:
        Altinn3CloudEvent(
            alternativesubject="altsubject",
            data="",
            datacontenttype="datatype",
            id="123",
            source="https://approved.mock",
            specversion="1.2.3",
            subject="testorg",
            type="an.instance.event",
            resource="urn:altinn:resource:app_ssb_skjema",
            resourceinstance="party/instans-uuid",
        )
        assert "Field 'time' must have a value for all non-validation events." in str(
            e.value
        )
        assert e.type == ValidationError


def test_create_instance_event_no_subject_error(mocker: MockerFixture):
    mocker.patch.dict(
        os.environ, {"APPROVED_EVENT_SOURCE_URL": "https://approved.mock"}, clear=True
    )
    with pytest.raises(ValueError) as e:
        Altinn3CloudEvent(
            alternativesubject="altsubject",
            data="",
            datacontenttype="datatype",
            id="123",
            source="https://approved.mock",
            specversion="1.2.3",
            time="littførlunsj",
            type="an.instance.event",
            resource="urn:altinn:resource:app_ssb_skjema",
            resourceinstance="party/instans-uuid",
        )
        assert (
            "Field 'subject' must have a value for all non-validation events."
            in str(e.value)
        )
        assert e.type == ValidationError


def test_create_instance_event_no_alt_subject_ok(mocker: MockerFixture):
    mocker.patch.dict(
        os.environ, {"APPROVED_EVENT_SOURCE_URL": "https://approved.mock"}, clear=True
    )
    Altinn3CloudEvent(
        data="",
        datacontenttype="datatype",
        id="123",
        source="https://approved.mock",
        specversion="1.2.3",
        subject="testorg",
        time="littførlunsj",
        type="an.instance.event",
        resource="urn:altinn:resource:app_ssb_skjema",
        resourceinstance="party/instans-uuid",
    )
    assert True
