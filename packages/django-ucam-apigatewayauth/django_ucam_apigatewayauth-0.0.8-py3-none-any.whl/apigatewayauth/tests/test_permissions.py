from unittest.mock import MagicMock, patch

from django.test import TestCase
from identitylib.identifiers import Identifier, IdentifierSchemes
from rest_framework.test import APIRequestFactory
from ucamlookup.ibisclient import IbisException

from apigatewayauth.authentication import APIGatewayAuthenticationDetails
from apigatewayauth.permissions import (
    Disallowed,
    HasAnyScope,
    IsResourceOwningPrincipal,
    SpecifiedPermission,
    get_permissions_for_request,
)

from .mocks.mock_ibis import MockIbisGroup
from .mocks.models import TestModel
from .mocks.permissions_spec import override_permission_spec


class PermissionsTestCase(TestCase):
    def compatAssertQuerySetEqual(self, *args, **kwargs):
        """
        Backwards compatibility function as TestCase class refactored assertQuerysetEqual to
        assertQuerySetEqual in Django v5.
        """
        if hasattr(self, "assertQuerysetEqual"):
            return self.assertQuerysetEqual(*args, **kwargs)
        return self.assertQuerySetEqual(*args, **kwargs)

    def setUp(self):
        super().setUp()

        self.view = MagicMock()
        self.object = MagicMock()

        self.client_auth_details = APIGatewayAuthenticationDetails(
            Identifier("abc", IdentifierSchemes.CRSID), set()
        )

    def request_with_auth(self, auth):
        request = APIRequestFactory().get("/")
        setattr(request, "auth", auth)
        return request

    def test_disallowed_permission_always_disallows(self):
        permission = Disallowed()

        for auth in [None, self.client_auth_details]:
            self.assertFalse(permission.has_permission(self.request_with_auth(auth), self.view))
            self.assertFalse(
                permission.has_object_permission(
                    self.request_with_auth(auth), self.view, self.object
                )
            )

    def test_is_resource_owning_principal_returns_true_when_authenticated(self):
        permission = IsResourceOwningPrincipal()

        self.assertFalse(permission.has_permission(self.request_with_auth(None), self.view))
        self.assertFalse(
            permission.has_object_permission(self.request_with_auth(None), self.view, self.object)
        )

        public_client_request = self.request_with_auth(self.client_auth_details)
        self.assertTrue(permission.has_permission(public_client_request, self.view))
        # the request should be flagged as needing limiting
        self.assertTrue(
            getattr(public_client_request, "should_limit_to_resource_owning_principal")
        )

    def test_is_resource_owning_principal_users_has_object_permission(self):
        permission = IsResourceOwningPrincipal()

        # should be false as the object passed in doesn't have a 'is_owned_by' property
        self.assertFalse(
            permission.has_object_permission(
                self.request_with_auth(self.client_auth_details), self.view, {}
            )
        )

        mock_object = MagicMock()
        mock_object.is_owned_by.return_value = False

        self.assertFalse(
            permission.has_object_permission(
                self.request_with_auth(self.client_auth_details), self.view, mock_object
            )
        )
        mock_object.is_owned_by.assert_called_with(self.client_auth_details.principal_identifier)

        mock_object.is_owned_by.return_value = True
        self.assertTrue(
            permission.has_object_permission(
                self.request_with_auth(self.client_auth_details), self.view, mock_object
            )
        )

    def test_get_queryset_for_principal_bails_for_unhandled_request(self):
        # bails early if request doesn't require filtering
        self.compatAssertQuerySetEqual(
            IsResourceOwningPrincipal.get_queryset_for_principal(
                self.request_with_auth(self.client_auth_details), TestModel
            ),
            TestModel.objects.all(),
        )

    def test_get_queryset_for_principal_returns_filtered_queryset(self):
        permission = IsResourceOwningPrincipal()

        request = self.request_with_auth(self.client_auth_details)

        # pass through `has_permission` to mark `should_limit_to_resource_owning_principal`
        # on the requests
        self.assertTrue(permission.has_permission(request, self.view))

        self.compatAssertQuerySetEqual(
            IsResourceOwningPrincipal.get_queryset_for_principal(request, TestModel),
            TestModel.get_queryset_for_principal(self.client_auth_details.principal_identifier),
        )

    def test_get_queryset_for_principal_returns_no_objects_if_no_request_auth(self):
        permission = IsResourceOwningPrincipal()

        request = APIRequestFactory().get("/")

        # `has_permission` should return false as we have no auth details on the request
        self.assertFalse(permission.has_permission(request, self.view))

        # Set should_limit_to_resource_owning_principal manually, which allows us to hit the
        # condition of having no principal whilst trying to get the queryset for a principal.
        # This should never really happen, but we handle the condition in the permission class
        # so it's worth a test.
        setattr(request, "should_limit_to_resource_owning_principal", True)

        # If we get the queryset for the principal we should get objects.none() as we do not have
        # a principal.
        self.compatAssertQuerySetEqual(
            IsResourceOwningPrincipal.get_queryset_for_principal(request, TestModel),
            TestModel.objects.none(),
        )

    def test_get_queryset_for_principal_throws_on_an_unknown_model(self):
        permission = IsResourceOwningPrincipal()

        request = self.request_with_auth(self.client_auth_details)
        self.assertTrue(permission.has_permission(request, self.view))

        # using get_queryset_for_principal without a model defining get_queryset_for_principal
        # should cause a value error with a desciption message
        with self.assertRaisesRegex(
            ValueError, "{} does not implement get_queryset_for_principal"
        ):
            IsResourceOwningPrincipal.get_queryset_for_principal(request, {})

    def test_has_any_scope(self):
        permission = HasAnyScope("a", "b.readonly")()

        for auth in [None, self.client_auth_details]:
            self.assertFalse(permission.has_permission(self.request_with_auth(auth), self.view))
            self.assertFalse(
                permission.has_object_permission(
                    self.request_with_auth(auth), self.view, self.object
                )
            )

        self.assertTrue(
            permission.has_permission(
                self.request_with_auth(
                    APIGatewayAuthenticationDetails(
                        Identifier("abc", IdentifierSchemes.CRSID), set(["b.readonly"])
                    )
                ),
                self.view,
            )
        )

        self.assertFalse(
            permission.has_object_permission(
                self.request_with_auth(
                    APIGatewayAuthenticationDetails(
                        Identifier("abc", IdentifierSchemes.CRSID), set(["abcd"])
                    )
                ),
                self.view,
                self.object,
            )
        )

    @patch("apigatewayauth.permissions.get_principals_with_permission")
    def test_has_specified_permission_return_false_if_not_matching(self, get_identities_mock):
        get_identities_mock.return_value = set(
            [
                Identifier("1000", IdentifierSchemes.STAFF_NUMBER),
                Identifier("abc123", IdentifierSchemes.CRSID),
            ]
        )
        permission = SpecifiedPermission("READ_BOOKS")()

        self.assertFalse(
            permission.has_permission(self.request_with_auth(self.client_auth_details), self.view)
        )
        self.assertFalse(
            permission.has_object_permission(
                self.request_with_auth(self.client_auth_details), self.view, {}
            )
        )
        get_identities_mock.assert_called_with("READ_BOOKS")

    @patch("apigatewayauth.permissions.get_principals_with_permission")
    def test_has_specified_permission_return_true_if_matching(self, get_identities_mock):
        get_identities_mock.return_value = set(
            [
                Identifier("1000", IdentifierSchemes.STAFF_NUMBER),
                self.client_auth_details.principal_identifier,
            ]
        )
        permission = SpecifiedPermission("READ_BOOKS")()

        self.assertTrue(
            permission.has_permission(self.request_with_auth(self.client_auth_details), self.view)
        )
        self.assertTrue(
            permission.has_object_permission(
                self.request_with_auth(self.client_auth_details), self.view, {}
            )
        )
        get_identities_mock.assert_called_with("READ_BOOKS")

    @patch("apigatewayauth.permissions.get_principals_with_permission")
    @patch("apigatewayauth.permissions.get_groups_with_permission")
    @patch("apigatewayauth.permissions.PersonMethods.getGroups")
    def test_does_not_query_lookup_groups_for_non_crsid_principal(
        self,
        get_groups_mock,
        get_groups_with_permission_mock,
        get_identities_mock,
    ):
        get_identities_mock.return_value = set(
            [
                Identifier("abc123", IdentifierSchemes.CRSID),
                Identifier("abc333", IdentifierSchemes.CRSID),
            ]
        )
        get_groups_with_permission_mock.return_value = set(
            [
                Identifier("1000", IdentifierSchemes.LOOKUP_GROUP),
            ]
        )
        permission = SpecifiedPermission("READ_MAGAZINES")()

        auth_details = APIGatewayAuthenticationDetails(
            Identifier("1", IdentifierSchemes.STAFF_NUMBER), set([])
        )

        self.assertFalse(
            permission.has_permission(self.request_with_auth(auth_details), self.view)
        )
        self.assertFalse(
            permission.has_object_permission(self.request_with_auth(auth_details), self.view, {})
        )
        get_identities_mock.assert_called_with("READ_MAGAZINES")

        # should not have queried for groups as our principal does not have a crsid identifier
        get_groups_mock.assert_not_called()

    @patch("apigatewayauth.permissions.get_principals_with_permission")
    @patch("apigatewayauth.permissions.get_groups_with_permission")
    @patch("apigatewayauth.permissions.PersonMethods.getGroups")
    def test_does_not_query_lookup_groups_if_no_lookup_groups_in_permissions_spec(
        self,
        get_groups_mock,
        get_groups_with_permission_mock,
        get_identities_mock,
    ):
        get_identities_mock.return_value = set(
            [
                Identifier("1000", IdentifierSchemes.STAFF_NUMBER),
                Identifier("bb123", IdentifierSchemes.CRSID),
            ]
        )
        get_groups_with_permission_mock.return_value = set()
        permission = SpecifiedPermission("READ_PAMPHLETS")()

        self.assertFalse(
            permission.has_permission(self.request_with_auth(self.client_auth_details), self.view)
        )
        get_identities_mock.assert_called_with("READ_PAMPHLETS")

        # should not have queried for groups as we do not have a lookup group in our
        # allowed identities list
        get_groups_mock.assert_not_called()

    @patch("apigatewayauth.permissions.get_principals_with_permission")
    @patch("apigatewayauth.permissions.get_groups_with_permission")
    @patch("apigatewayauth.permissions.PersonMethods.getGroups")
    def test_will_return_true_if_principal_is_in_specified_lookup_group(
        self,
        get_groups_mock,
        get_groups_with_permission_mock,
        get_identities_mock,
    ):
        get_identities_mock.return_value = set([Identifier("cc123", IdentifierSchemes.CRSID)])
        get_groups_with_permission_mock.return_value = set(
            [Identifier("1001", IdentifierSchemes.LOOKUP_GROUP)]
        )
        permission = SpecifiedPermission("READ_THE_NEWS")()
        get_groups_mock.return_value = [MockIbisGroup("1001"), MockIbisGroup("1002")]

        self.assertTrue(
            permission.has_permission(self.request_with_auth(self.client_auth_details), self.view)
        )
        get_identities_mock.assert_called_with("READ_THE_NEWS")

        # should have queried Lookup for the principal's groups
        get_groups_mock.assert_called_with(
            scheme="crsid",
            identifier=self.client_auth_details.principal_identifier.value,
        )

        # querying again returns true without going to Lookup due to caching the result
        get_groups_mock.reset_mock()
        self.assertTrue(
            permission.has_permission(self.request_with_auth(self.client_auth_details), self.view)
        )
        get_groups_mock.assert_not_called()

    @patch("apigatewayauth.permissions.get_principals_with_permission")
    @patch("apigatewayauth.permissions.get_groups_with_permission")
    @patch("apigatewayauth.permissions.PersonMethods.getGroups")
    def test_will_return_false_if_principal_is_not_in_specified_lookup_group(
        self,
        get_groups_mock,
        get_groups_with_permission_mock,
        get_identities_mock,
    ):
        get_identities_mock.return_value = set([Identifier("dd123", IdentifierSchemes.CRSID)])
        get_groups_with_permission_mock.return_value = set(
            [Identifier("10101", IdentifierSchemes.LOOKUP_GROUP)]
        )
        permission = SpecifiedPermission("READ_THE_ROOM")()
        get_groups_mock.return_value = [MockIbisGroup("1001"), MockIbisGroup("1002")]

        self.assertFalse(
            permission.has_permission(self.request_with_auth(self.client_auth_details), self.view)
        )
        get_identities_mock.assert_called_with("READ_THE_ROOM")

        # should have queried Lookup for the principal's groups
        get_groups_mock.assert_called_with(
            scheme="crsid",
            identifier=self.client_auth_details.principal_identifier.value,
        )

    @patch("apigatewayauth.permissions.get_principals_with_permission")
    @patch("apigatewayauth.permissions.get_groups_with_permission")
    @patch("apigatewayauth.permissions.PersonMethods.getGroups")
    def test_will_return_false_if_unable_to_read_lookup_groups(
        self,
        get_groups_mock,
        get_groups_with_permission_mock,
        get_identities_mock,
    ):
        get_identities_mock.return_value = set(
            [
                Identifier("ee123", IdentifierSchemes.CRSID),
            ]
        )
        get_groups_with_permission_mock.return_value = set(
            [
                Identifier("2000", IdentifierSchemes.LOOKUP_GROUP),
            ]
        )
        permission = SpecifiedPermission("READ_THE_FUTURE")()

        def throw_ibis_error(*args, **kwargs):
            error = ValueError("failed")
            setattr(error, "message", "failed")  # ibis exception needs a 'message' attribute
            raise IbisException(error)

        get_groups_mock.side_effect = throw_ibis_error

        self.assertFalse(
            permission.has_permission(self.request_with_auth(self.client_auth_details), self.view)
        )
        get_identities_mock.assert_called_with("READ_THE_FUTURE")

        # should have queried Lookup for the principal's groups
        get_groups_mock.assert_called_with(
            scheme="crsid",
            identifier=self.client_auth_details.principal_identifier.value,
        )

    @override_permission_spec(
        {
            "DATA_READER": {
                "principals": {
                    str(Identifier("abc44", IdentifierSchemes.CRSID)),
                    str(Identifier("abc55", IdentifierSchemes.CRSID)),
                }
            },
            "DATA_OWNER": {"principals": {str(Identifier("abc44", IdentifierSchemes.CRSID))}},
        }
    )
    def test_get_permissions_for_request(self):
        """
        Test that `get_permissions_for_request` returns correctly based on the user authenticated
        on the request.

        """

        mock_request = APIRequestFactory().get("/")
        setattr(mock_request, "auth", None)

        # expect an empty list to be returned if no auth details provided
        self.assertListEqual(get_permissions_for_request(mock_request), [])

        # if we have a principal not in our permissions spec we should get an empty list
        mock_request.auth = APIGatewayAuthenticationDetails(
            Identifier("abc123", IdentifierSchemes.CRSID), []
        )
        self.assertListEqual(get_permissions_for_request(mock_request), [])

        # abc55 should be shown as a `DATA_READER`
        mock_request.auth = APIGatewayAuthenticationDetails(
            Identifier("abc55", IdentifierSchemes.CRSID), []
        )
        self.assertListEqual(get_permissions_for_request(mock_request), ["DATA_READER"])

        # abc44 should be shown as a `DATA_READER` and `DATA_WRITER`
        mock_request.auth = APIGatewayAuthenticationDetails(
            Identifier("abc44", IdentifierSchemes.CRSID), []
        )
        self.assertListEqual(
            get_permissions_for_request(mock_request), ["DATA_OWNER", "DATA_READER"]
        )
