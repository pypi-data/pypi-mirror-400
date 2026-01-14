KEYS = [
    "ra_nummer",
    "skjema_id",
    "app_id",
    "periode_id",
    "periode_aar",
    "pulje_id",
    "utsending_id",
    "prefill_meta_id",
    "utsendingsmal_id",
]

KEYMAP = {
    "ra_nummer": "RA_NUMMER",
    "skjema_id": "SKJEMA_ID",
    "app_id": "APP_ID",
    "periode_id": "PERIODE_ID",
    "pulje_id": "PULJE_ID",
    "utsending_id": "UTSENDING_ID",
    "prefill_meta_id": "SKJEMA_PREFILL_META_ID",
    "utsendingsmal_id": "UTSENDINGSMAL_ID",
}


def build(key: str, body: dict) -> str:
    form_key = KEYMAP[key]

    return f"{form_key}:{body[key]}"


def build_from_param(key: str, param: str or int) -> str:
    form_key = KEYMAP[key]
    return f"{form_key}:{param}"
