#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as gt

from django_quotas.config import DjangoQuotasConfig as cfg


class BaseQuotaUsageModel(models.Model):
    class Meta:
        abstract = True
        db_table = f"{cfg.TABLE_PREFIX}_quota_usage"
        verbose_name = gt("Quota Usage")
        unique_together = ("account_id", "feature_name", "point_in_time")
        indexes = (
            models.Index(fields=["account_id", "feature_name", "point_in_time"]),
            models.Index(fields=["account_id", "point_in_time"]),
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_id = models.CharField(verbose_name="Account", null=False, blank=False, db_index=True)
    feature_name = models.CharField(max_length=300, null=False, blank=False)
    point_in_time = models.DateTimeField(null=False, blank=False)
    usage_count = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self) -> str:
        return f"QuotaUsage(account={self.account_id}, feature={self.feature_name}, ts={self.point_in_time})"
