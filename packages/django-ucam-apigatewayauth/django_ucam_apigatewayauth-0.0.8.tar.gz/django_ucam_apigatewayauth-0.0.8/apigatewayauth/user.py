from django.contrib.auth.models import AnonymousUser

from .authentication import APIGatewayAuthenticationDetails


class APIGatewayUser(AnonymousUser):
    """
    A Django user representing the authenticated principal. This user is not
    backed by a database object and so they can have no permissions in the
    Django sense.
    """

    def __init__(self, auth: APIGatewayAuthenticationDetails):
        super().__init__()
        self.username = self.id = self.pk = str(auth.principal_identifier)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.username
