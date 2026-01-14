#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
from functools import cached_property
from typing import TYPE_CHECKING, Final

from django.conf import settings

from django_quotas.utils import get_model_by_name

if TYPE_CHECKING:
    from django_quotas.backends.db.base_models import BaseQuotaUsageModel


__all__ = ["__DjangoQuotasDbConfig", "DjangoQuotasDbConfig"]


class __DjangoQuotasDbConfig:
    """Configuration accessor for DB-backed quotas implementation."""

    SETTINGS_PREFIX: Final[str] = "DJANGO_QUOTAS"

    @cached_property
    def QUOTA_USAGE_MODEL(self) -> str:
        """Return the full model name for the quota usage model.

        @return: Model name string.
        """
        return getattr(settings, f"{self.SETTINGS_PREFIX}_DB_USAGE_MODEL_NAME", "django_quotas_db.QuotaUsageModel")

    @cached_property
    def quota_usage_cls(self) -> type["BaseQuotaUsageModel"]:
        """Return the quota usage model class.

        @return: Quota usage model class.
        """
        return get_model_by_name(self.QUOTA_USAGE_MODEL)  # type: ignore


DjangoQuotasDbConfig = __DjangoQuotasDbConfig()
