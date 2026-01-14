from typing import List, Any, Tuple, Dict, Optional
from functools import wraps
from cachetools import TTLCache
from cachetools.keys import hashkey
from threading import Lock
import os

import json

from fastapi import Request, HTTPException
import ssb_altinn3_util.security.authenticator_constants as const
import ssb_altinn3_util.security.helpers.jwt_helper as jwt_helper
import ssb_altinn3_util.security.helpers.keybuilder as keybuilder
import ssb_altinn3_util.security.helpers.auth_service_client as auth_service_client
from ssb_altinn3_util.security.authorization_result import AuthorizationResult


enforce_token_validation = bool(os.getenv("VALIDATE_TOKEN", None))


def authorize(
    require_role: str,
    enable_form_access: bool = False,
    root_element: bool = False,
    cache_seconds: int = 0,
):
    """
    Authorization component to be used as a decorator far an api-endpoint in a FastAPI application.  Requires the
    following to function properly:
    Env variable AUTH_SERVICE_URL must be set with the base url to the authorization service endpoint.
    The role-argument must be one of the roles defined in authenticator_constants (in ssb_altinn3_util.security).

    If token is not validated before reaching the API (i.e. via a service mesh, gateway or similar), the token must
    be validated explicitly to maintain security.  To enable token verification, the following environment variables
    must be set for the service:

    VALIDATE_TOKEN - any value will enable token verification.  For clarity, set it to "enabled" or something similar
    AUTH_AUTHORITY_URL - base url (including realm if used) for the STS-provider
    VALID_AUDIENCES - a string of accepted audiences in the token, separated by commas
    TRUSTED_ISSUER - string containing the trusted issuer of the token.  (Often similar to AUTH_AUTHORITY_URL)

    Note that if form access should be validated, set the attribue 'enable_form_access' to True in the decorator (this
    attribute will default to False if not set, so setting it to False will have no effect other than a visual
    indication that form access will not be validated for the endpoint):

    @app.get("/stuff")
    @authorize(required_role=<required_role(s)>, enable_form_access=True)
    def do_stuff(form: str, request: Request):
        ....

    Multiple roles can be specified as well, if an endpoint is available for more than one role.  This is done by
    adding the roles as a string, separating the different roles with a comma.  Note that this will grant access
    if ANY of the roles are owned by the user.  Example:

    @app.get("/stuff")
    @authorize(required_role="<role1>,<role2>")
    def do_stuff(form: str, request: Request):
        ....

    """
    roles: List[str] = require_role.split(",")

    for r in roles:
        if r not in const.VALID_ROLES:
            raise ValueError(f"Supplied role '{r}' is not a valid role!")

    cache: TTLCache or None = None
    cache_lock = Lock()

    if cache_seconds > 0:
        # Enforce a maximum cache duration of 5 minutes
        if cache_seconds > 300:
            cache_seconds = 300
        cache = TTLCache(maxsize=100, ttl=cache_seconds)

    def _get_cached_item(key: tuple):
        if cache is None:
            return None
        with cache_lock:
            return cache.get(key)

    def _set_cache_item(key: tuple, val: AuthorizationResult):
        if cache is None:
            return
        with cache_lock:
            cache[key] = val

    def _create_cache_key(
        user_email: str,
        form_access_key: Optional[str] = None,
        is_root_element: Optional[bool] = None,
    ):
        return hashkey(user_email, form_access_key, is_root_element)

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            # Get request object
            request = _extract_request(args, kwargs)

            access_token = _extract_token(request=request)

            # validate token if required
            if enforce_token_validation:
                user_email = jwt_helper.validate_token(token=access_token)
            else:
                # Get user from token
                user_email = jwt_helper.get_user_email_from_token(access_token)

            if not user_email:
                raise HTTPException(
                    status_code=401,
                    detail="Unable to find user email in supplied token!",
                )

            if enable_form_access:
                form_access_key = _build_form_access_key(request=request)
                if form_access_key is None:
                    raise HTTPException(
                        status_code=403, detail="Unable to determine form access key."
                    )
            else:
                form_access_key = None

            # Verify required role
            result = _validate_role_access(user_email, form_access_key, root_element)

            request.state.user_email = user_email
            request.state.allowed_forms_read = result.allowed_forms_read
            request.state.allowed_forms_write = result.allowed_forms_write

            # Proceed to wrapped function
            return func(*args, **kwargs)

        def _get_from_args(args: Tuple[Any, ...]) -> Request or None:
            for arg in args:
                if isinstance(arg, Request):
                    return arg
            else:
                return None

        def _get_from_kwargs(kwargs: Dict[str, Any]) -> Request or None:
            for kwarg in kwargs.values():
                if isinstance(kwarg, Request):
                    return kwarg
            else:
                return None

        def _validate_role_access(
            user_email: str,
            form_access_key: Optional[str] = None,
            is_root_element: Optional[bool] = None,
        ) -> AuthorizationResult:
            cache_key = _create_cache_key(
                user_email=user_email,
                form_access_key=form_access_key,
                is_root_element=is_root_element,
            )
            result: AuthorizationResult or None = _get_cached_item(cache_key)

            if result is not None:
                return result

            for role in roles:
                result = auth_service_client.verify_access(
                    user_email=user_email,
                    requested_role=role,
                    form_access_key=form_access_key,
                    is_root_element=is_root_element,
                )
                if result.access_granted:
                    _set_cache_item(cache_key, result)
                    return result
            if result is None:
                raise HTTPException(
                    status_code=400, detail="Unable to verify supplied roles."
                )
            if not result.access_granted:
                raise HTTPException(
                    status_code=result.status_code, detail=result.error_message
                )
            return result

        def _build_form_access_key(request: Request) -> str or None:
            key: str or None = None

            if request.method == "DELETE":
                key = _get_non_body_key(request=request)
            elif request.method in ["POST", "PUT"]:
                try:
                    key = _get_key_from_body(request=request)

                    if key is None:
                        key = _get_non_body_key(request=request)
                except Exception as e:
                    raise HTTPException(status_code=403, detail=str(e))
            return key

        def _get_non_body_key(request: Request) -> str or None:
            key = _get_key_from_path(request=request)

            if key is not None:
                return key

            return _get_key_from_query_params(request=request)

        def _get_key_from_body(request: Request) -> str or None:
            if not hasattr(request, "_body"):
                return None

            body = json.loads(request._body.decode("UTF-8"))

            for key in keybuilder.KEYS:
                if key in body:
                    return keybuilder.build(key=key, body=body)
            return None

        def _get_key_from_path(request: Request) -> str or None:
            params = request.path_params

            for key in keybuilder.KEYS:
                if key in params:
                    return keybuilder.build_from_param(key=key, param=params[key])

            return None

        def _get_key_from_query_params(request: Request) -> str or None:
            params = request.query_params._dict

            for key in keybuilder.KEYS:
                if key in params:
                    return keybuilder.build_from_param(key=key, param=params[key])

            return None

        def _extract_token(request: Request) -> str:
            auth_header = request.headers.get("authorization", None)

            if not auth_header:
                raise HTTPException(
                    status_code=401, detail="Authorization header missing"
                )

            parts = auth_header.split(" ")

            if parts[0].lower() != "bearer":
                raise HTTPException(
                    status_code=401, detail="Token must be passed as 'Bearer'."
                )

            if len(parts) != 2:
                raise HTTPException(
                    status_code=401,
                    detail="Extra elements detected in Authorization header",
                )

            return parts[1]

        def _extract_request(args, kwargs):
            request: Request = _get_from_args(args)
            if request is None:
                request = _get_from_kwargs(kwargs)
            if request is None:
                raise ValueError(f"Unable to extract request object!")
            return request

        return inner

    return wrapper
