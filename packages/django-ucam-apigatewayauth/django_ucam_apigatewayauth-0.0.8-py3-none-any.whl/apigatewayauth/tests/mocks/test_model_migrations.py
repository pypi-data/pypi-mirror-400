from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[str] = []

    operations = [
        migrations.CreateModel(
            name="TestModel",
            fields=[
                (
                    "name",
                    models.TextField(primary_key=True, serialize=False, verbose_name="Name"),
                ),
                ("isAdmin", models.BooleanField(verbose_name="Is Admin")),
                (
                    "principal_identifier",
                    models.TextField(verbose_name="Principal identifier"),
                ),
            ],
        ),
    ]
