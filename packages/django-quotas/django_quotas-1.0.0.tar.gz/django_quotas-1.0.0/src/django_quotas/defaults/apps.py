#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#

__all__ = ["QuotasDefaultsConfig"]

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as gt


class QuotasDefaultsConfig(AppConfig):
    """Django AppConfig for the django_quotas application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_quotas.defaults"
    label = "django_quotas_defaults"
    verbose_name = gt("Quotas")
    default = True
