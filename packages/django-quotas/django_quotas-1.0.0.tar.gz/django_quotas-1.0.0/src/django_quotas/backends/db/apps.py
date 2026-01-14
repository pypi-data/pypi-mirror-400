#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
__all__ = ["QuotasDbConfig"]

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as gt


class QuotasDbConfig(AppConfig):
    """Django AppConfig for the django_quotas.backend.sdb application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_quotas.backends.db"
    label = "django_quotas_db"
    verbose_name = gt("Quotas DB Backend")
    default = True
