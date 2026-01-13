from logging import getLogger
from typing import Set

from django.core.cache import cache
from identitylib.identifiers import IdentifierSchemes
from rest_framework import permissions, request
from ucamlookup.ibisclient import IbisException, PersonMethods
from ucamlookup.utils import get_connection

from .authentication import APIGatewayAuthenticationDetails
from .permissions_spec import (
    get_groups_with_permission,
    get_permission_spec,
    get_principals_with_permission,
)

LOG = getLogger(__name__)


class Disallowed(permissions.BasePermission):
    """
    A permissions class which disallows all access, this is used as the default permissions
    class to stop routes being added which accidentally expose data.

    """

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class IsResourceOwningPrincipal(permissions.BasePermission):
    """
    A permissions class which ensures that the client represents a principal who is limited
    to accessing only resources they own.

    """

    message = "Please authenticate as the owning user using the API Gateway."

    @staticmethod
    def get_queryset_for_principal(request, base_object):
        """
        A helper method which filters the given object's queryset to the owning principal
        if required

        """
        if not getattr(request, "should_limit_to_resource_owning_principal", False):
            return base_object.objects.all()
        if not isinstance(getattr(request, "auth", None), APIGatewayAuthenticationDetails):
            return base_object.objects.none()

        if not callable(getattr(base_object, "get_queryset_for_principal", None)):
            raise ValueError(f"{base_object} does not implement get_queryset_for_principal")
        return base_object.get_queryset_for_principal(request.auth.principal_identifier)

    def has_permission(self, request, view):
        # we cannot determine permissions ownership on list routes, but rely on
        # `get_queryset_for_principal` to be used to filter the queryset appropriately
        if isinstance(getattr(request, "auth", None), APIGatewayAuthenticationDetails):
            setattr(request, "should_limit_to_resource_owning_principal", True)
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if not isinstance(getattr(request, "auth", None), APIGatewayAuthenticationDetails):
            return False

        is_owned_by = getattr(obj, "is_owned_by", None)
        if not callable(is_owned_by):
            LOG.warn(f"Unable to determine ownership for {obj}")
            return False

        return is_owned_by(request.auth.principal_identifier)


def HasAnyScope(*required_scopes):
    class HasAnyScopesPermission(permissions.BasePermission):
        """
        A permissions class which enforces that the given request has any of the given scopes.

        """

        message = f'Request must have one of the following scope(s) {" ".join(required_scopes)}'

        def has_permission(self, request, view):
            request_scopes = getattr(getattr(request, "auth", {}), "scopes", set())
            return len(set(required_scopes) & request_scopes) > 0

        def has_object_permission(self, request, view, obj):
            return self.has_permission(request, view)

    return HasAnyScopesPermission


def SpecifiedPermission(permission: str):
    class HasSpecifiedPermission(permissions.BasePermission):
        """
        A permissions class which ensures that the principal has the correct permissions
        within the permissions specification.

        """

        message = f"Authenticated principal does not have permission {permission}"

        def has_permission(self, request, view):
            principals_with_permission = get_principals_with_permission(permission)
            if request.auth.principal_identifier in principals_with_permission:
                return True

            if request.auth.principal_identifier.scheme != IdentifierSchemes.CRSID:
                LOG.warn("Can only determine group membership for principals identified by CRSID")
                return False

            # special case for people identified by crsid - check whether they are in a
            # lookup group within our list of identities for permission
            groups_with_permission = get_groups_with_permission(permission)
            lookup_group_ids = set(
                [
                    identifier.value
                    for identifier in groups_with_permission
                    if identifier.scheme == IdentifierSchemes.LOOKUP_GROUP
                ]
            )

            if not lookup_group_ids:
                return False

            return self.is_in_any_lookup_group(
                request.auth.principal_identifier.value, lookup_group_ids
            )

        def has_object_permission(self, request, view, obj):
            return self.has_permission(request, view)

        def is_in_any_lookup_group(self, crsid: str, group_ids: Set[str]) -> bool:
            """
            Determine whether a person identified by a crsid is a member of any of the lookup
            groups provided. Caches the result for 5 minutes to speed up subsequent responses.

            """
            cache_key = f'{crsid}_in_{",".join(group_ids)}'
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response

            is_in_group = False
            try:
                group_list = PersonMethods(get_connection()).getGroups(
                    scheme="crsid", identifier=crsid
                )
                is_in_group = any(
                    (group.groupid for group in group_list if group.groupid in group_ids)
                )
            except IbisException as err:
                LOG.warn(f"Failed to get Lookup groups for {crsid} due to {err}")
                return False

            cache.set(cache_key, is_in_group, timeout=600)
            return is_in_group

    return HasSpecifiedPermission


def get_permissions_for_request(req: request.Request):
    """
    Returns a list of permissions which the request's principal has been granted.
    The permissions will be key any of the keys from the permissions spec, where the
    principal is included within the principals or groups sections.

    """

    return (
        [
            permission_name
            for permission_name in get_permission_spec().keys()
            if SpecifiedPermission(permission_name)().has_permission(req, None)
        ]
        if isinstance(req.auth, APIGatewayAuthenticationDetails)
        else []
    )
