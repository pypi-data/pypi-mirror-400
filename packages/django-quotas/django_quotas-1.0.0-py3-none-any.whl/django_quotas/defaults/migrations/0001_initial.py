#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
import uuid

from django.db import migrations, models
import django.db.models.deletion

import django_quotas.base.dto
from django_quotas.config import DjangoQuotasConfig as cfg


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(cfg.QUOTA_RELATED_ACCOUNT_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DefaultQuotaModel",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("owner_tag", models.CharField(blank=True, max_length=300, null=True)),
                ("feature_name", models.CharField(max_length=300)),
                ("hourly_limit", models.IntegerField(blank=True, null=True)),
                ("daily_limit", models.IntegerField(blank=True, null=True)),
                ("monthly_limit", models.IntegerField(blank=True, null=True)),
                ("total_limit", models.IntegerField(blank=True, null=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quotas",
                        to=cfg.QUOTA_RELATED_ACCOUNT_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Account Quota",
                "db_table": "django_quotas_quota",
                "indexes": [models.Index(fields=["account", "feature_name"], name="django_quot_account_348168_idx")],
                "unique_together": {("account", "feature_name")},
            },
        ),
    ]
