from datetime import datetime, date
from pydantic import BaseModel, computed_field
from typing import Optional


from ssb_altinn3_util.constants.enums import (
    UtsendingEnhetType,
    UtsendingFormat,
    MottakerType,
    UtsendingsKanal,
)


class PeriodeResponseModel(BaseModel):
    id: int
    skjema_id: int
    periode_type: Optional[str] = None
    periode_nr: Optional[int] = None
    periode_aar: Optional[int] = None
    periode_dato: Optional[date] = None
    delreg_nr: Optional[int] = None
    enhet_type: Optional[str] = None
    vis_oppgavebyrde: str
    vis_brukeropplevelse: str
    har_skjemadata: str
    journalnummer: Optional[str] = None
    endret_dato: datetime
    endret_av: str


class PuljeResponseModel(BaseModel):
    id: int
    periode_id: int
    pulje_nr: Optional[int] = None
    altinn_tilgjengelig: Optional[datetime] = None
    altinn_svarfrist: Optional[date] = None
    tvangsmulkt_svarfrist: Optional[date] = None
    send_si: Optional[date] = None

    ra_nummer: Optional[str] = None
    versjon: Optional[int] = None
    undersokelse_nr: Optional[str] = None
    periode_type: Optional[str] = None
    periode_nr: Optional[int] = None
    periode_aar: Optional[int] = None

    endret_dato: datetime
    endret_av: str


class UtsendingResponseModel(BaseModel):
    id: int
    pulje_id: int
    pulje_nr: Optional[int] = None
    utsendingstype_id: Optional[int] = None
    utsendingstype_navn: Optional[str] = None
    utsendingstype_kortnavn: Optional[str] = None
    trigger: str
    test: bool
    altinn_uts_tidspunkt: Optional[datetime] = None
    krever_godkjenning: Optional[bool] = False
    status: Optional[str] = None
    endret_dato: datetime
    endret_av: str


class SkjemaResponseModel(BaseModel):
    id: int
    ra_nummer: str
    versjon: int
    undersokelse_nr: str
    datamodell: Optional[str] = None
    beskrivelse: Optional[str] = None
    navn_nb: Optional[str] = None
    navn_nn: Optional[str] = None
    navn_en: Optional[str] = None
    infoside: Optional[str] = None
    eier: Optional[str] = None
    kun_sky: str
    gyldig_fra: date
    gyldig_til: Optional[date] = None
    endret_dato: datetime
    endret_av: str

    # perioder: Optional[List[PeriodeResponseModel]]


class SkjemaPrefillMetaResponseModel(BaseModel):
    id: int
    skjema_id: int
    navn: str
    sti: Optional[str] = None
    tittel: Optional[str] = None
    type: str
    min: Optional[int] = None
    maks: Optional[int] = None
    obligatorisk: Optional[bool] = False
    dublett_sjekk: Optional[bool] = False
    stat_navn: Optional[str] = None
    kommentar: Optional[str] = None
    endret_dato: datetime
    endret_av: str

    @computed_field
    def sti_navn(self) -> str:
        return f"{self.sti}.{self.navn}" if self.sti is not None else self.navn


class UtsendingstypeResponseModel(BaseModel):
    id: int
    navn: str
    kortnavn: Optional[str] = None
    enhet_type: UtsendingEnhetType
    utsendingsformat: Optional[UtsendingFormat] = None
    mottakere: MottakerType
    meldingsheader: Optional[str] = None
    kanal: UtsendingsKanal
    endret_dato: datetime
    endret_av: str


class UtsendingsmalResponseModel(BaseModel):
    id: int
    skjema_id: int
    utsendingstype_id: int
    utsendingstype_navn: Optional[str] = None
    utsendingstype_kortnavn: Optional[str] = None
    malnavn: str
    malversjon: Optional[int] = None
    vedlegg_malnavn: Optional[str] = None
    gyldig_fra: date
    gyldig_til: Optional[date] = None
    endret_dato: datetime
    endret_av: str
