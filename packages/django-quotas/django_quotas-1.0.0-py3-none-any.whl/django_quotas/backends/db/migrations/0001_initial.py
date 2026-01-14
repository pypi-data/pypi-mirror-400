#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#

import uuid

from django.db import migrations, models
import django.db.models.deletion

from django_quotas.config import DjangoQuotasConfig as cfg


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(cfg.QUOTA_RELATED_ACCOUNT_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="QuotaUsageModel",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("feature_name", models.CharField(max_length=300)),
                ("point_in_time", models.DateTimeField()),
                ("usage_count", models.IntegerField(default=0)),
                (
                    "account",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=cfg.QUOTA_RELATED_ACCOUNT_MODEL),
                ),
            ],
            options={
                "verbose_name": "Quota Usage",
                "db_table": "django_quotas_quota_usage",
                "indexes": [
                    models.Index(
                        fields=["account", "feature_name", "point_in_time"], name="django_quot_account_b2afd6_idx"
                    ),
                    models.Index(fields=["account", "point_in_time"], name="django_quot_account_6a9881_idx"),
                ],
                "unique_together": {("account", "feature_name", "point_in_time")},
            },
        ),
    ]
