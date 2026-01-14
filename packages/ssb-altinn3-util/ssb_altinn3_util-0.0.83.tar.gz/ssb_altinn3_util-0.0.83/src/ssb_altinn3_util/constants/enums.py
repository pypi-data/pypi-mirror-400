from enum import Enum


class UtsendingEnhetType(str, Enum):
    Foretak = "FRTK"
    Bedrift = "BEDR"
    Person = "PERS"
    SkjemaEnhet = "SKJEMA_ENHET"


class MottakerType(str, Enum):
    Alle = "ALLE"
    Besvart = "BESVART"
    IkkeBesvart = "IKKE_BESVART"


class UtsendingFormat(str, Enum):
    pdf = "PDF"
    text = "TXT"
    html = "HTML"
    json = "JSON"
    md = "MD"
    xml = "XML"


class UtsendingsKanal(str, Enum):
    altinn = "altinn"
    epost = "epost"
    sms = "sms"
