from functools import wraps
from tempfile import NamedTemporaryFile
from typing import Dict

import yaml
from django.test import override_settings


def override_permission_spec(permissions_spec: Dict[str, Dict[str, set[str]]]):
    """
    A decorator which allows the permissions specification to be mocked, allowing a
    permission to only be enabled for the given identities.

    """

    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            with NamedTemporaryFile("w+") as temp_file:
                yaml.dump(permissions_spec, temp_file.file)
                with override_settings(PERMISSIONS_SPECIFICATION_URL=temp_file.name):
                    func(*args, **kwargs)

        return wrapped_function

    return decorator
