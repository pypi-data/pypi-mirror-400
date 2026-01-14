#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
from functools import cached_property
from typing import TYPE_CHECKING, Final, cast

from django.conf import settings
from django.db import models

from django_quotas.utils import get_class_by_name, get_model_by_name

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin

    from django_quotas.models import BaseQuotaModel


__all__ = ["DjangoQuotasConfig"]


class __DjangoQuotasConfig:
    """Configuration accessor for django_quotas settings and related models."""

    SETTINGS_PREFIX: Final[str] = "DJANGO_QUOTAS"

    @cached_property
    def TABLE_PREFIX(self) -> str:
        """Return the table prefix for quota tables.

        :return: Table prefix string.
        """
        return getattr(settings, f"{self.SETTINGS_PREFIX}_TABLE_PREFIX", "django_quotas")

    @cached_property
    def QUOTA_MODEL(self) -> str:
        """Get the full model name for the quota model.

        :return: Model name string.
        """
        return getattr(settings, f"{self.SETTINGS_PREFIX}_QUOTA_MODEL_NAME", "django_quotas.defaults.QuotaModel")

    @cached_property
    def QUOTA_RELATED_ACCOUNT_MODEL(self) -> str:
        """Get the related account model name for quotas.

        :return: Related account model name string.
        """
        return getattr(settings, f"{self.SETTINGS_PREFIX}_QUOTA_RELATED_ACCOUNT_MODEL_NAME", "auth.User")

    @cached_property
    def BASE_ADMIN_CLASS(self) -> str:
        """Get the base admin class for quota admin interfaces.

        :return: Base admin class name string
        """
        return getattr(settings, f"{self.SETTINGS_PREFIX}_BASE_ADMIN_CLASS", "django.contrib.admin.ModelAdmin")

    @cached_property
    def quota_cls(self) -> type["BaseQuotaModel"]:
        """Get the quota model class.

        :return: Quota model class.
        """
        return get_model_by_name(self.QUOTA_MODEL)  # type: ignore

    @cached_property
    def quota_related_account_cls(self) -> type[models.Model]:
        """Get the related account model class for quotas.

        :return: Related account model class.
        """
        return get_model_by_name(self.QUOTA_RELATED_ACCOUNT_MODEL)

    def base_admin_cls(self) -> type["ModelAdmin"]:
        """Get the base admin class for quota admin interfaces.

        :return: Base admin class.
        """
        return cast(type["ModelAdmin"], get_class_by_name(self.BASE_ADMIN_CLASS))


DjangoQuotasConfig = __DjangoQuotasConfig()
