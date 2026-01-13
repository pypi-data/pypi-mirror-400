from typing import Dict, List, Set

from django.conf import settings
from django.core.cache import cache
from geddit import geddit
from identitylib.identifiers import Identifier
from yaml import safe_load

PERMISSIONS_CACHE_KEY = "__PERMISSION_CACHE__"


def get_permission_spec() -> Dict[str, Dict[str, List]]:
    """
    Returns the permissions spec - expected to be a mapping of permission name to a list of
    identifiers representing people or service identities who have the given permission.

    """

    cached_entry = cache.get(PERMISSIONS_CACHE_KEY)
    if cached_entry:
        return cached_entry

    permissions_spec = safe_load(geddit(settings.PERMISSIONS_SPECIFICATION_URL))
    # Cache the permissions spec for 12 hours. We expect the application to be redeployed
    # when the permissions spec is updated, so it is safe to cache this for a long period
    # of time.
    cache.set(PERMISSIONS_CACHE_KEY, permissions_spec, timeout=43200)

    return permissions_spec


def get_principals_with_permission(permission_name: str) -> Set[Identifier]:
    """
    Returns a set of Identifiers representing people or service identities which have
    the given permission according to the permissions specification.

    """
    return set(
        map(
            lambda identifier_str: Identifier.from_string(identifier_str, find_by_alias=True),
            get_permission_spec().get(permission_name, {}).get("principals", []),
        )
    )


def get_groups_with_permission(permission_name: str) -> Set[Identifier]:
    """
    Returns a set of Identifiers representing groups which indicate membership gives the
    users or service accounts the specified permission.

    """
    return set(
        map(
            lambda identifier_str: Identifier.from_string(identifier_str, find_by_alias=True),
            get_permission_spec().get(permission_name, {}).get("groups", []),
        )
    )
