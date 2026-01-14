from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional
import os


def make_test_api(app: FastAPI):
    os.environ["NAIS_APP_NAME"] = "test-test"

    from ssb_altinn3_util.security.role_authorization import authorize

    class AccessTestModel(BaseModel):
        ra_nummer: Optional[str] = None
        skjema_id: Optional[int] = None
        app_id: Optional[str] = None
        periode_id: Optional[int] = None
        periode_aar: Optional[int] = None
        periode_type: Optional[str] = None
        periode_nr: Optional[int] = None
        pulje_id: Optional[int] = None
        utsending_id: Optional[int] = None
        message: str

    @app.get("/hello")
    @authorize(require_role="admin")
    def hello(request: Request) -> str:
        return "hello"

    @app.post("/enforce")
    @authorize(require_role="admin", enable_form_access=True)
    def post_call_with_form_access_enforcement(
        request: Request, model: AccessTestModel
    ):
        return f"Received: '{model.message}'"

    @app.post("/no_body/{app_id}")
    @authorize(require_role="admin", enable_form_access=True)
    def post_call_without_body(request: Request, app_id: str):
        if not hasattr(request, "_body"):
            return "OK!"
        return "Not Ok!"

    @app.put("/enforce")
    @authorize(require_role="admin", enable_form_access=True)
    def post_call_with_form_access_enforcement(
        request: Request, model: AccessTestModel
    ):
        return f"Received: '{model.message}'"

    @app.delete("/ra_nummer/{ra_nummer}")
    @authorize(require_role="admin", enable_form_access=True)
    def delete_ra_nummer(ra_nummer: str, request: Request):
        return f"ra_nummer: {ra_nummer}"

    @app.delete("/skjema/{skjema_id}")
    @authorize(require_role="admin", enable_form_access=True)
    def delete_skjema(skjema_id: int, request: Request):
        return f"skjema_id: {skjema_id}"

    @app.delete("/app/{app_id}")
    @authorize(require_role="admin", enable_form_access=True)
    def delete_app_id(app_id: str, request: Request):
        return f"app_id: {app_id}"

    @app.delete("/periode/{periode_id}")
    @authorize(require_role="admin", enable_form_access=True)
    def delete_periode0(periode_id: int, request: Request):
        return f"periode_id: {periode_id}"

    @app.delete("/pulje/{pulje_id}")
    @authorize(require_role="admin", enable_form_access=True)
    def delete_pulje(pulje_id: int, request: Request):
        return f"pulje_id: {pulje_id}"

    @app.delete("/utsending/{utsending_id}")
    @authorize(require_role="admin", enable_form_access=True)
    def delete_utsending(utsending_id: int, request: Request):
        return f"utsending_id: {utsending_id}"

    @app.delete("/prefill_meta/{prefill_meta_id}")
    @authorize(require_role="admin", enable_form_access=True)
    def delete_prefill_meta(prefill_meta_id: int, request: Request):
        return f"prefill_meta_id: {prefill_meta_id}"

    @app.delete("/utsendingsmal/{utsendingsmal_id}")
    @authorize(require_role="admin", enable_form_access=True)
    def delete_utsendingsmal(utsendingsmal_id: int, request: Request):
        return f"utsendingsmal_id: {utsendingsmal_id}"

    @app.delete("/query_test_ra_nummer")
    @authorize(require_role="admin", enable_form_access=True)
    def query_test_ra(ra_nummer: str, request: Request):
        return f"ra_nummer: {ra_nummer}"

    @app.delete("/query_test_skjema")
    @authorize(require_role="admin", enable_form_access=True)
    def query_test_ra(skjema_id: int, request: Request):
        return f"skjema_id: {skjema_id}"

    client = TestClient(app)

    return app, client
