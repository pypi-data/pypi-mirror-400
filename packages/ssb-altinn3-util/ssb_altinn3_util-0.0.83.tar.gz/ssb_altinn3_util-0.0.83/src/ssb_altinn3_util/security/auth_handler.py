import os
import configparser
import logging
from threading import Lock

from ssb_altinn3_util.security.helpers.token_validators import (
    BaseTokenValidator,
    ValidatorConfig,
    LabIdValidator,
    AuthSSBValidator,
)

logger = logging.getLogger()


class AuthHandler:
    _instance: "AuthHandler" = None
    _lock: Lock = Lock()
    validators: dict[str, BaseTokenValidator]
    initialized: bool

    @staticmethod
    def get_instance():
        with AuthHandler._lock:
            if AuthHandler._instance is None:
                AuthHandler._instance = AuthHandler()
        return AuthHandler._instance

    def __init__(self):
        self.validators = {}
        self.initialized = False
        self.init()

    def init(self):
        auth_parser = configparser.ConfigParser()

        config_file_path = os.path.join(os.getcwd(), "app/auth.config")

        if not os.path.exists(config_file_path):
            logger.warning("Unable to configure AuthHandler: No auth.config EXISTS!")
            return

        auth_parser.read(config_file_path)
        suv_environment = os.getenv("NAIS_APP_NAME").split("-")[0]

        if not suv_environment:
            logger.warning(
                "Unable to configure AuthHandler: Can't determine runtime SUV environment!"
            )
            return

        providers = auth_parser["providers"]["keys"].split(",")

        if not providers:
            logger.warning(
                "Unable to configure AuthHandler: No providers defined in auth.config"
            )
            return

        envs = auth_parser["providers"]["envs"].split(",")

        environment = suv_environment if suv_environment in envs else None

        if not environment:
            logger.warning(
                f"Unable to configure AuthHandler: No providers configured for environment '{suv_environment}'"
            )
            return

        for p in providers:
            prv = auth_parser[f"provider_{p}_{environment}"]
            config = ValidatorConfig(
                authority=prv["authority"],
                issuer=prv["trusted_issuer"],
                audiences=prv["audiences"],
            )

            if p == "labId":
                self.validators[config.issuer] = LabIdValidator(config=config)
            elif p == "authSSB":
                self.validators[config.issuer] = AuthSSBValidator(config=config)
            else:
                logger.error(
                    "Unsupported auth provider.  Unable to configure authentication"
                )
                continue
            logger.info(f"Configured auth for provider '{p}'")
        self.initialized = True

    def get_validator(self, issuer: str) -> BaseTokenValidator:
        return self.validators.get(issuer, None)
