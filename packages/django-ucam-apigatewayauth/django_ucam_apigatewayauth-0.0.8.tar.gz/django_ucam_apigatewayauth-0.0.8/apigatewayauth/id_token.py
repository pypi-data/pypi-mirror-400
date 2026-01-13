"""
Utilities for verifying id tokens.
"""
from typing import Any, Iterable, Optional

import cachecontrol
import requests
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import Request
from google.auth.transport.requests import Request as RequestsRequest
from google.oauth2 import id_token

__all__ = ["verify_id_token_for_api_backend", "InvalidIdTokenError"]


def _default_caching_request() -> Request:
    """
    Return a google.auth.transport.Request sub-class which caches requests for id token
    certificates.

    Uses the approach documented at
    https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.id_token.html.

    """
    session = requests.session()
    cached_session = cachecontrol.CacheControl(session)
    return RequestsRequest(session=cached_session)


# Default HTTP transport used to fetch public keys for verifying tokens.
_DEFAULT_CACHING_REQUEST = _default_caching_request()

# List of Google service accounts which represent the API gateway identity.
_DEFAULT_EXPECTED_AUTHORISED_PARTIES = ["api-gateway@api-meta-2555105a.iam.gserviceaccount.com"]

# Default URL used to fetch certificates corresponding to JWT signing keys
_DEFAULT_CERTS_URL = "https://www.googleapis.com/oauth2/v1/certs"

# Default list of issuers trusted to issue identity tokens.
_DEFAULT_TRUSTED_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


class InvalidIdTokenError(ValueError):
    """
    Exception raised if token verification fails. The exception message describes the reason that
    the token failed verification.
    """


def verify_id_token_for_api_backend(
    token: str,
    expected_audiences: str | list[str] | tuple[str],
    *,
    request: Optional[Request] = None,
    expected_authorised_parties: Optional[Iterable[str]] = None,
    certs_url: Optional[str] = None,
    trusted_issuers: Optional[Iterable[str]] = None,
) -> dict[str, Any]:
    """
    Verify an incoming authentication token from the Gateway sent to an API backend. Use this
    function when implementing API backends.

    :param token: id token passed to the backend by the Gateway.
    :param expected_audiences: a list of expected audiences for id token. For Cloud Run-hosted
        backends this is the base URL of the application.
    :param request: HTTP transport implementation. If `None` then a default implementation based on
        the :py:mod:`requests` library is used. Note that certificates are fetched on each call to
        this function and so the transport implementation should support caching. This is the case
        for the default implementation.
    :param expected_authorised_parties: the "azp" claim in the id token must match one of the
        strings in this iterable for the token to be verified. If `None` then a list of known API
        Gateway identities is used.
    :param certs_url: URL used to fetch certificates. If omitted, a URL corresponding to Google
        identity tokens is used.
    :param trusted_issuers: iterable of strings specifying trusted id token issuers. If omitted, a
        set of issuers corresponding to Google is used.
    :returns: a dictionary containing the id token payload.
    """
    request = request if request is not None else _DEFAULT_CACHING_REQUEST
    expected_authorised_parties = (
        set(expected_authorised_parties)
        if expected_authorised_parties is not None
        else _DEFAULT_EXPECTED_AUTHORISED_PARTIES
    )
    certs_url = certs_url if certs_url is not None else _DEFAULT_CERTS_URL
    trusted_issuers = (
        set(trusted_issuers) if trusted_issuers is not None else _DEFAULT_TRUSTED_ISSUERS
    )

    try:
        payload = id_token.verify_token(
            token, request, audience=expected_audiences, certs_url=certs_url
        )
    except GoogleAuthError as e:
        raise InvalidIdTokenError(str(e)) from e
    if payload["iss"] not in trusted_issuers:
        raise InvalidIdTokenError(f"'{payload['iss']}' is not a trusted id token issuer")

    authorized_party = payload.get("azp", "")
    if payload.get("azp", "") not in expected_authorised_parties:
        raise InvalidIdTokenError(
            f"Authorized party {authorized_party!r} not one of {expected_authorised_parties!r}."
        )

    return payload
