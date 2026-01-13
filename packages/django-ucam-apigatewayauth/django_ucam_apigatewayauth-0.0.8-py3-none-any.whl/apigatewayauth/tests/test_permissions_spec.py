from unittest.mock import patch

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
from identitylib.identifiers import Identifier, IdentifierSchemes

from apigatewayauth.permissions_spec import (
    get_groups_with_permission,
    get_permission_spec,
    get_principals_with_permission,
)


class PermissionSpecTestCase(TestCase):
    def setUp(self):
        super().setUp()
        cache.clear()  # clear the cache between tests

    @patch("apigatewayauth.permissions_spec.geddit")
    def test_will_return_parsed_permissions_spec_with_cache(self, geddit_mock):
        geddit_mock.return_value = """
            CARD_DATA_READERS:
                principals:
                    - abc123@v1.person.identifiers.cam.ac.uk
                    - 1234@application.api.apps.cam.ac.uk
                groups:
                    - 1001@groups.lookup.cam.ac.uk
        """

        expected_permission_spec = {
            "CARD_DATA_READERS": {
                "principals": [
                    str(Identifier("abc123", IdentifierSchemes.CRSID)),
                    str(Identifier("1234", IdentifierSchemes.API_GATEWAY_APPLICATION)),
                ],
                "groups": [
                    str(Identifier("1001", IdentifierSchemes.LOOKUP_GROUP)),
                ],
            }
        }
        self.assertEqual(get_permission_spec(), expected_permission_spec)
        geddit_mock.assert_called_with(settings.PERMISSIONS_SPECIFICATION_URL)

        geddit_mock.reset_mock()

        # ensure that getting the permissions spec again does not use geddit as the cached
        # result is used
        self.assertEqual(get_permission_spec(), expected_permission_spec)
        geddit_mock.assert_not_called()

    @patch("apigatewayauth.permissions_spec.geddit")
    def test_can_query_specific_permission(self, geddit_mock):
        geddit_mock.return_value = """
            CARD_DATA_READERS:
                principals:
                    - 1234@application.api.apps.cam.ac.uk
                    - abc123@v1.person.identifiers.cam.ac.uk
                groups:
                    - 1001@groups.lookup.cam.ac.uk
            CARD_DATA_WRITERS:
                principals:
                    - abc234@v1.person.identifiers.cam.ac.uk
        """

        self.assertEqual(
            get_principals_with_permission("CARD_DATA_READERS"),
            {
                Identifier("1234", IdentifierSchemes.API_GATEWAY_APPLICATION),
                Identifier("abc123", IdentifierSchemes.CRSID),
            },
        )
        geddit_mock.assert_called_with(settings.PERMISSIONS_SPECIFICATION_URL)
        geddit_mock.reset_mock()

        self.assertEqual(
            get_groups_with_permission("CARD_DATA_READERS"),
            {Identifier("1001", IdentifierSchemes.LOOKUP_GROUP)},
        )
        # should not be called as we have cached the spec
        geddit_mock.assert_not_called()

        self.assertEqual(
            get_principals_with_permission("CARD_DATA_WRITERS"),
            {Identifier("abc234", IdentifierSchemes.CRSID)},
        )

        self.assertEqual(get_groups_with_permission("CARD_DATA_WRITERS"), set())

        self.assertEqual(get_groups_with_permission("CARD_DATA_ADMINS"), set())
        self.assertEqual(get_principals_with_permission("CARD_DATA_ADMINS"), set())
