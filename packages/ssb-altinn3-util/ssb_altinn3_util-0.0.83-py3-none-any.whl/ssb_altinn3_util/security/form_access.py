from typing import List

from fastapi import Request, HTTPException

import ssb_altinn3_util.security.authenticator_constants as constants


class FormAccessValidator:
    """
    Authorization component for validating user access to a given form, divided by read and write access.
    Form access must be validated in the actual endpoint code, calling the verify_read_access or verify_write_access
    function of the FormAccessValidator.  Example:

    @app.get("/stuff")
    @authorize(required_role=<required_role(s)>)
    def do_stuff(form: str, request: Request):
        validator = FormAccessValidator(request=request)
        validator.verify_form_read_access(form=form)
        ....

    The validator verifies the form against the form access lists stored in the request.state by the
    authorize-decorator (ssb_altinn3_util.security.role_authorization.authorize).  If this decorator is not used prior
    to instantiating the FormAccessValidator the verification will fail automatically and access will always be denied.

    """

    allowed_forms_read: List[str]
    allowed_forms_write: List[str]

    def __init__(self, request: Request):
        self.allowed_forms_read = []
        self.allowed_forms_write = []
        if hasattr(request.state, "allowed_forms_read"):
            self.allowed_forms_read = request.state.allowed_forms_read
        if hasattr(request.state, "allowed_forms_write"):
            self.allowed_forms_write = request.state.allowed_forms_write

    def verify_form_read_access(self, form: str) -> bool:
        allowed_forms = set(self.allowed_forms_read + self.allowed_forms_write)
        if constants.FORM_ACCESS_ALL in allowed_forms or form in allowed_forms:
            return True
        raise HTTPException(
            status_code=403, detail=f"User has insufficient access to form '{form}'"
        )

    def verify_form_write_access(self, form: str) -> bool:
        if (
            constants.FORM_ACCESS_ALL in self.allowed_forms_write
            or form in self.allowed_forms_write
        ):
            return True
        raise HTTPException(
            status_code=403, detail=f"User has insufficient access to form '{form}'"
        )
