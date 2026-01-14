#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#

__all__ = ["BaseQuotaModel", "QuotaModelMetaclass"]

import abc
import uuid

from django.db import models

from django_quotas.base.dto import Quota, ValuePerBucket


class BaseQuotaModel(models.Model):
    """Base model for quotas that can be converted to Quota interface when needed."""

    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_tag = models.CharField(max_length=300, null=True, blank=True)
    feature_name = models.CharField(max_length=300, null=False, blank=False)
    hourly_limit = models.IntegerField(null=True, blank=True)
    daily_limit = models.IntegerField(null=True, blank=True)
    monthly_limit = models.IntegerField(null=True, blank=True)
    total_limit = models.IntegerField(null=True, blank=True)

    @property
    def get_limits(self) -> ValuePerBucket:
        """Return the quota limits as a ValuePerBucket instance.

        :return: ValuePerBucket with limits for each bucket.
        """
        return ValuePerBucket(
            hourly=self.hourly_limit, daily=self.daily_limit, monthly=self.monthly_limit, total=self.total_limit
        )


class QuotaModelMetaclass(type(models.Model), type(Quota)):  # type: ignore[misc]
    """Specific metaclass to satisfy django migrations creating class in a non-standard way."""

    pass
