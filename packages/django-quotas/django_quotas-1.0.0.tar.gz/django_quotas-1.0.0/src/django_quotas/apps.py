#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#

__all__ = ["QuotasConfig"]

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as gt


class QuotasConfig(AppConfig):
    """Django AppConfig for the django_quotas application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_quotas"
    label = "django_quotas"
    verbose_name = gt("Quotas")
    default = True
