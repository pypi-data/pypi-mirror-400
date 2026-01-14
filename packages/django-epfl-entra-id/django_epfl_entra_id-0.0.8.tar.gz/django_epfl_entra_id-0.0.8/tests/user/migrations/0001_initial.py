import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        max_length=128,
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        max_length=150,
                        unique=True,
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True,
                        max_length=30,
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True,
                        max_length=30,
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                    ),
                ),
                (
                    "sciper",
                    models.CharField(
                        blank=True,
                        max_length=10,
                        unique=True,
                    ),
                ),
            ],
        ),
    ]
