from datetime import datetime, date, timezone

from ssb_altinn3_util.constants.enums import (
    UtsendingEnhetType,
    MottakerType,
    UtsendingFormat,
    UtsendingsKanal,
)
from ssb_altinn3_util.models.skjemadata.skjemadata_response_models import (
    UtsendingstypeResponseModel,
    UtsendingsmalResponseModel,
)
from ssb_altinn3_util.models.skjemadata.skjemadata_request_models import (
    UtsendingstypeRequestModel,
    UtsendingsmalRequestModel,
)


def test_utsendingstype_request_model_ok():
    UtsendingstypeRequestModel(
        navn="test",
        utsendingsformat=UtsendingFormat.text,
        enhet_type=UtsendingEnhetType.Person,
        mottakere=MottakerType.Alle,
        kanal=UtsendingsKanal.altinn,
        endret_dato=datetime.now(timezone.utc),
        endret_av="abc",
    )
    assert True


def test_utsendingstype_response_model_ok():
    UtsendingstypeResponseModel(
        id=1,
        navn="test",
        utsendingsformat=UtsendingFormat.text,
        enhet_type=UtsendingEnhetType.Person,
        mottakere=MottakerType.Alle,
        kanal=UtsendingsKanal.altinn,
        endret_dato=datetime.now(timezone.utc),
        endret_av="abc",
    )
    assert True


def test_utsendingsmal_request_model_ok():
    UtsendingsmalRequestModel(
        id=1,
        skjema_id=2,
        utsendingstype_id=3,
        utsendingstype_navn="testtype",
        malnavn="testmal",
        malversjon=1,
        gyldig_fra=date.today(),
        gyldig_til=date.today(),
        endret_dato=datetime.now(timezone.utc),
        endret_av="abc",
    )
    assert True


def test_utsendingsmal_response_model_ok():
    UtsendingsmalResponseModel(
        id=1,
        skjema_id=2,
        utsendingstype_id=3,
        # utsendingstype_navn="testtype",
        malnavn="testmal",
        malversjon=1,
        gyldig_fra=date.today(),
        gyldig_til=date.today(),
        endret_dato=datetime.now(timezone.utc),
        endret_av="abc",
    )
    assert True
