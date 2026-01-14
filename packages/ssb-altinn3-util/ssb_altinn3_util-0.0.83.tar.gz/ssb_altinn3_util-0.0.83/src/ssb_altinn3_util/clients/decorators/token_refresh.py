def refresh_token_cache(func):
    """
    Decorator intended for use with the "AltinnApiClient" ONLY.  Placed here since there already
    was a folder for decorators under the clients module.
    Accesses args[0] (self-parameter of instance functions) and calls refresh token, updating the
    cached token if necessary.
    """

    def inner(*args, **kwargs):
        args[0].refresh_token()
        return func(*args, **kwargs)

    return inner
