# This import needs to be removed but to do so breaks compatibility with
# existing users. See comments in apigatewayauth.auth.APIGatewayAuthentication.
from .authentication import (  # noqa: F401
    APIGatewayAuthentication,
    APIGatewayAuthenticationDetails,
)

default_app_config = "apigatewayauth.apps.APIGatewayAuthConfig"
