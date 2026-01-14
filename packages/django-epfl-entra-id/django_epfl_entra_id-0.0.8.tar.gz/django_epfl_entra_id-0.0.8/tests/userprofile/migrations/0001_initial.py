from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "sciper",
                    models.CharField(blank=True, max_length=10, null=True),
                ),
                (
                    "classe",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "statut",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "user",
                    models.OneToOneField(
                        related_name="profile",
                        null=True,
                        to="auth.User",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
    ]
