from time import sleep
from functools import wraps
import logging

logger = logging.getLogger()


def exception_handler(client_name: str, retries: int = 1):
    def client_wrapper(func):
        @wraps(func)
        def inner_function(*args, **kwargs):
            nonlocal retries
            attempts = retries
            while attempts > 0:
                attempts = attempts - 1
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    if attempts == 0:
                        raise Exception(
                            f"Client '{client_name}' failed to fetch with error:\n{e}"
                        )
                    logger.warning(
                        f"Fetch token failed (client '{client_name}') with error: {e}"
                    )
                    logger.warning(f"Remaining attempts: {attempts}")
                    sleep(1)

        return inner_function

    return client_wrapper
