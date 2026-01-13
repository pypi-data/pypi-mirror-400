from dataclasses import dataclass
from logging import getLogger
from typing import Optional, Set

from django.conf import settings
from identitylib.identifiers import Identifier
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from .id_token import InvalidIdTokenError, verify_id_token_for_api_backend

LOG = getLogger(__name__)


@dataclass(eq=True)
class APIGatewayAuthenticationDetails:
    """
    A dataclass representing the authentication information passed from the API Gateway.

    """

    principal_identifier: Identifier
    scopes: Set[str]
    app_id: Optional[str] = None
    client_id: Optional[str] = None


class APIGatewayAuthentication(authentication.BaseAuthentication):
    """
    An Authentication provider which interprets the headers provided by the API Gateway.

    This library expects to only be used within an application that is deployed behind and can
    only be invoked by the API Gateway, and therefore relies on the fact that the headers
    provided are authoritative.

    """

    def authenticate(self, request: Request):
        # This import is needed here because APIGatewayUser references
        # AnonymousUser from django.contrib.auth which, in turn, means that
        # applications have to be ready at import time.
        #
        # This file is imported from apigatewayauth/__init__.py and
        # apigatewayauth is imported at application configure time. The net
        # upshot is that we cannot import directly or indirectly from
        # django.contrib.auth at the top of this file and have to do it here.
        #
        # We can't remove the imports at the top of apigatewayauth/__init__.py
        # because we have users of this library which set the DRF default
        # authentication class to "apigatewayauth.APIGatewayAuthentication".
        #
        # These users need to be fixed up to use
        # "apigatewayauth.authentication.APIGatewayAuthentication" instead and
        # then we can move this import back where it belongs.
        from .user import APIGatewayUser

        if not request.META.get("HTTP_X_API_ORG_NAME", None):
            # bail early if we look like we're not being called by the API Gateway
            return None

        try:
            # We should have "Bearer ..." in the authorization header.
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                raise AuthenticationFailed("Bearer token not present")

            # Extract the id token from the API Gateway for verification.
            _, token = auth_header.split(" ")

            expected_audiences = getattr(
                settings,
                "API_GATEWAY_JWT_EXPECTED_AUDIENCE",
                [request.build_absolute_uri("/"), request.build_absolute_uri("/").rstrip("/")],
            )

            trusted_issuers = getattr(settings, "API_GATEWAY_JWT_TRUSTED_ISSUERS", None)
            expected_authorised_parties = getattr(
                settings, "API_GATEWAY_JWT_EXPECTED_AUTHORISED_PARTIES", None
            )
            try:
                verify_id_token_for_api_backend(
                    token,
                    expected_audiences,
                    certs_url=getattr(settings, "API_GATEWAY_JWT_ISSUER_CERTS_URL", None),
                    trusted_issuers=trusted_issuers,
                    expected_authorised_parties=expected_authorised_parties,
                )
            except InvalidIdTokenError as e:
                LOG.info(f"Incoming API token failed verification: {e}")
                raise AuthenticationFailed("Invalid API Gateway token") from e
        except AuthenticationFailed as e:
            if getattr(settings, "API_GATEWAY_ENFORCE_ID_TOKEN_VERIFICATION", False):
                raise e
            else:
                LOG.warning(
                    "API_GATEWAY_ENFORCE_ID_TOKEN_VERIFICATION is False. "
                    f"Allowing incoming request with invalid authentication: {e}"
                )

        if not request.META.get("HTTP_X_API_OAUTH2_USER", None):
            raise AuthenticationFailed("Could not authenticate using x-api-* headers")

        try:
            principal_identifier = Identifier.from_string(
                request.META["HTTP_X_API_OAUTH2_USER"], find_by_alias=True
            )
        except Exception:
            raise AuthenticationFailed("Invalid principal identifier")

        auth = APIGatewayAuthenticationDetails(
            principal_identifier=principal_identifier,
            scopes=set(filter(bool, request.META.get("HTTP_X_API_OAUTH2_SCOPE", "").split(" "))),
            # the following will only be populated for confidential clients
            app_id=request.META.get("HTTP_X_API_DEVELOPER_APP_ID", None),
            client_id=request.META.get("HTTP_X_API_OAUTH2_CLIENT_ID", None),
        )
        user = APIGatewayUser(auth)
        return user, auth
