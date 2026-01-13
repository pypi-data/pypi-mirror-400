import secrets
from unittest import mock

from django.test import TestCase, override_settings
from google.auth.exceptions import GoogleAuthError
from identitylib.identifiers import Identifier, IdentifierSchemes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory

from apigatewayauth.authentication import (
    APIGatewayAuthentication,
    APIGatewayAuthenticationDetails,
)


@override_settings(API_GATEWAY_ENFORCE_ID_TOKEN_VERIFICATION=True)
class APIGatewayAuthTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.request_factory = APIRequestFactory()
        self.auth = APIGatewayAuthentication()

        # Patch the token verification function. The default side effect is to check that the token
        # matches self.expected_token.
        self.expected_token = secrets.token_urlsafe()

        def verify_token(token: str, *args, **kwargs):
            if token != self.expected_token:
                raise GoogleAuthError("Token did not match mock token")
            return {
                "iss": "https://accounts.google.com",
                "azp": "api-gateway@api-meta-2555105a.iam.gserviceaccount.com",
            }

        verify_token_patcher = mock.patch(
            "google.oauth2.id_token.verify_token", side_effect=verify_token
        )
        self.mock_verify_token = verify_token_patcher.start()
        self.addCleanup(verify_token_patcher.stop)

    def request_with_headers(self, headers={}, *, include_authorization=True):
        parsed_headers = {
            f'HTTP_{key.upper().replace("-", "_")}': value for key, value in headers.items()
        }
        if include_authorization:
            parsed_headers["HTTP_AUTHORIZATION"] = f"Bearer {self.expected_token}"
        return self.request_factory.get("/", **parsed_headers)

    def test_bails_early_without_api_org(self):
        self.assertIsNone(
            self.auth.authenticate(self.request_with_headers({"Accept": "application/json"}))
        )

    def test_throws_without_auth_details(self):
        with self.assertRaisesMessage(
            AuthenticationFailed, "Could not authenticate using x-api-* headers"
        ):
            self.auth.authenticate(self.request_with_headers({"x-api-org-name": "test"}))

    def test_throws_without_principal_identifier(self):
        with self.assertRaisesMessage(
            AuthenticationFailed, "Could not authenticate using x-api-* headers"
        ):
            self.auth.authenticate(
                self.request_with_headers(
                    {"x-api-org-name": "test", "x-api-developer-app-class": "public"}
                )
            )

    def test_throws_with_bad_principal_identifier(self):
        with self.assertRaisesMessage(AuthenticationFailed, "Invalid principal identifier"):
            self.auth.authenticate(
                self.request_with_headers(
                    {
                        "x-api-org-name": "test",
                        "x-api-developer-app-class": "public",
                        "x-api-oauth2-user": "Monty Dawson",
                    }
                )
            )

    def test_can_use_any_identifier_scheme_in_principal_identifier(self):
        for scheme in IdentifierSchemes.get_registered_schemes():
            _, auth = self.auth.authenticate(
                self.request_with_headers(
                    {
                        "x-api-org-name": "test",
                        "x-api-developer-app-class": "public",
                        "x-api-oauth2-user": str(Identifier("1000", scheme)),
                    }
                )
            )
            self.assertEqual(auth.principal_identifier, Identifier("1000", scheme))

    def test_throws_with_unknown_identifier_type(self):
        with self.assertRaisesMessage(AuthenticationFailed, "Invalid principal identifier"):
            self.auth.authenticate(
                self.request_with_headers(
                    {
                        "x-api-org-name": "test",
                        "x-api-developer-app-class": "public",
                        "x-api-oauth2-user": "wgd23@gmail.com",
                    }
                )
            )

    def test_returns_client_details_for_valid_auth(self):
        user, auth = self.auth.authenticate(
            self.request_with_headers(
                {
                    "x-api-org-name": "test",
                    "x-api-developer-app-class": "public",
                    "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                }
            )
        )
        self.assertEqual(user.id, str(Identifier("a123", IdentifierSchemes.CRSID)))

        self.assertEqual(
            auth,
            APIGatewayAuthenticationDetails(
                Identifier("a123", IdentifierSchemes.CRSID),
                set(),
                None,
                None,
            ),
        )

    def test_returns_authenticated_non_anonymous_user(self):
        user, _ = self.auth.authenticate(
            self.request_with_headers(
                {
                    "x-api-org-name": "test",
                    "x-api-developer-app-class": "public",
                    "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                }
            )
        )
        self.assertFalse(user.is_anonymous)
        self.assertTrue(user.is_authenticated)

    def test_will_pass_through_scopes(self):
        _, auth = self.auth.authenticate(
            self.request_with_headers(
                {
                    "x-api-org-name": "test",
                    "x-api-developer-app-class": "public",
                    "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                    "x-api-oauth2-scope": (
                        "https://api.apps.cam.ac.uk/a.readonly https://api.apps.cam.ac.uk/b"
                    ),
                }
            )
        )

        self.assertEqual(
            auth,
            APIGatewayAuthenticationDetails(
                Identifier("a123", IdentifierSchemes.CRSID),
                set(
                    [
                        "https://api.apps.cam.ac.uk/a.readonly",
                        "https://api.apps.cam.ac.uk/b",
                    ]
                ),
                None,
                None,
            ),
        )

    def test_will_pass_through_app_and_client_ids(self):
        _, auth = self.auth.authenticate(
            self.request_with_headers(
                {
                    "x-api-org-name": "test",
                    "x-api-developer-app-class": "confidential",
                    "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                    "x-api-oauth2-scope": (
                        "https://api.apps.cam.ac.uk/a.readonly https://api.apps.cam.ac.uk/b"
                    ),
                    "x-api-developer-app-id": "app-uuid-mock",
                    "x-api-oauth2-client-id": "client-id-uuid-mock",
                }
            )
        )

        self.assertEqual(
            auth,
            APIGatewayAuthenticationDetails(
                Identifier("a123", IdentifierSchemes.CRSID),
                set(
                    [
                        "https://api.apps.cam.ac.uk/a.readonly",
                        "https://api.apps.cam.ac.uk/b",
                    ]
                ),
                "app-uuid-mock",
                "client-id-uuid-mock",
            ),
        )

    def test_fails_authentication_if_no_header_present(self):
        with self.assertRaisesMessage(AuthenticationFailed, "Bearer token not present"):
            self.auth.authenticate(
                self.request_with_headers(
                    {
                        "x-api-org-name": "test",
                        "x-api-developer-app-class": "public",
                        "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                    },
                    include_authorization=False,
                )
            )

    def test_fails_with_invalid_token(self):
        self.mock_verify_token.side_effect = GoogleAuthError("token-failed-verification")
        with self.assertRaisesMessage(AuthenticationFailed, "Invalid API Gateway token"):
            self.auth.authenticate(
                self.request_with_headers(
                    {
                        "x-api-org-name": "test",
                        "x-api-developer-app-class": "public",
                        "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                    }
                )
            )

    @override_settings(
        API_GATEWAY_JWT_EXPECTED_AUDIENCE="https://audience.invalid/",
        API_GATEWAY_JWT_ISSUER_CERTS_URL="https://issuer.invalid/certs",
    )
    def test_verify_token_passed_expected_audience_and_certs_url(self):
        self.assertIsNotNone(
            self.auth.authenticate(
                self.request_with_headers(
                    {
                        "x-api-org-name": "test",
                        "x-api-developer-app-class": "public",
                        "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                    }
                )
            )
        )
        self.mock_verify_token.assert_called_once()
        self.assertEqual(self.mock_verify_token.call_args[0][0], self.expected_token)
        self.assertEqual(
            self.mock_verify_token.call_args[1]["audience"], "https://audience.invalid/"
        )
        self.assertEqual(
            self.mock_verify_token.call_args[1]["certs_url"], "https://issuer.invalid/certs"
        )

    def test_default_audience(self):
        _, auth = self.auth.authenticate(
            self.request_with_headers(
                {
                    "x-api-org-name": "test",
                    "x-api-developer-app-class": "public",
                    "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                }
            )
        )
        self.mock_verify_token.assert_called_once()
        self.assertEqual(self.mock_verify_token.call_args[0][0], self.expected_token)
        self.assertEqual(
            set(self.mock_verify_token.call_args[1]["audience"]),
            {"http://testserver/", "http://testserver"},
        )

    def test_bad_id_token(self):
        with self.assertRaisesMessage(AuthenticationFailed, "Invalid API Gateway token"):
            self.auth.authenticate(
                self.request_with_headers(
                    {
                        "x-api-org-name": "test",
                        "x-api-developer-app-class": "public",
                        "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                        "Authorization": f"Bearer {secrets.token_urlsafe()}",
                    },
                    include_authorization=False,
                )
            )

    @override_settings(API_GATEWAY_JWT_TRUSTED_ISSUERS=["https://issuer.invalid/"])
    def test_bad_id_token_issuer(self):
        with self.assertRaisesMessage(AuthenticationFailed, "Invalid API Gateway token"):
            self.auth.authenticate(
                self.request_with_headers(
                    {
                        "x-api-org-name": "test",
                        "x-api-developer-app-class": "public",
                        "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                    }
                )
            )

    @override_settings(API_GATEWAY_JWT_EXPECTED_AUTHORISED_PARTIES=["gateway@gateway.invalid"])
    def test_bad_azp_claim(self):
        with self.assertRaisesMessage(AuthenticationFailed, "Invalid API Gateway token"):
            self.auth.authenticate(
                self.request_with_headers(
                    {
                        "x-api-org-name": "test",
                        "x-api-developer-app-class": "public",
                        "x-api-oauth2-user": str(Identifier("a123", IdentifierSchemes.CRSID)),
                    }
                )
            )
