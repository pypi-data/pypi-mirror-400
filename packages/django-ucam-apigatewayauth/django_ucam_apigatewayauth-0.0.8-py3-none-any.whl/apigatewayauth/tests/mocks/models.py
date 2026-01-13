from django.db import models


class TestModel(models.Model):
    """
    A test model to allow us to test functionality which requires a model instance to be passed in.

    """

    @staticmethod
    def get_queryset_for_principal(principal_identifier):
        return TestModel.objects.filter(
            principal_identifier__iexact=principal_identifier.value,
        )

    name = models.TextField("Name", "name", primary_key=True)
    is_admin = models.BooleanField("Is Admin", "isAdmin")
    principal_identifier = models.TextField("Principal identifier")
