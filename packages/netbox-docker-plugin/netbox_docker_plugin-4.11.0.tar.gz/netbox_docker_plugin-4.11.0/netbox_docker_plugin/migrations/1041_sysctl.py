# pylint: disable=C0103
# pylint: disable=R0801
"""Migration file"""

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Migration file"""

    dependencies = [
        ("netbox_docker_plugin", "1040_alter_container_log_driver"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sysctl",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        max_length=255,
                        validators=[
                            django.core.validators.MinLengthValidator(limit_value=1),
                            django.core.validators.MaxLengthValidator(limit_value=255),
                        ],
                    ),
                ),
                (
                    "value",
                    models.CharField(
                        blank=True,
                        max_length=4095,
                        validators=[
                            django.core.validators.MaxLengthValidator(limit_value=4095)
                        ],
                    ),
                ),
                (
                    "container",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sysctls",
                        to="netbox_docker_plugin.container",
                    ),
                ),
            ],
            options={
                "ordering": ("container", "key"),
                "constraints": [
                    models.UniqueConstraint(
                        models.F("key"),
                        models.F("container"),
                        name="netbox_docker_plugin_sysctl_unique_key_container'",
                    )
                ],
            },
        ),
    ]
