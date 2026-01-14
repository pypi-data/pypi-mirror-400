#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
__all__ = ("DefaultQuotaModel",)

from typing import cast
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as gt

from django_quotas.config import DjangoQuotasConfig as cfg
from django_quotas.models import BaseQuotaModel, QuotaModelMetaclass


class DefaultQuotaModel(BaseQuotaModel, metaclass=QuotaModelMetaclass):
    """Model for actual quota assigned to a user."""

    class Meta:
        db_table = f"{cfg.TABLE_PREFIX}_quota"
        verbose_name = gt("Account Quota")
        unique_together = ("account", "feature_name")
        indexes = (models.Index(fields=["account", "feature_name"]),)

    account: models.Model = models.ForeignKey(  # type: ignore[assignment,call-arg]
        cfg.QUOTA_RELATED_ACCOUNT_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="quotas",
        db_index=True,
        swappable=True,
    )

    def __str__(self) -> str:
        return f"Quota(id={self.pk}, feature={self.feature_name})"
