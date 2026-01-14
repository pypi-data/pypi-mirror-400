#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
from django.contrib import admin

from django_quotas.config import DjangoQuotasConfig as cfg
from django_quotas.defaults.models import DefaultQuotaModel


@admin.register(DefaultQuotaModel)
class DefaultQuotaAdmin(cfg.base_admin_cls()):  # type: ignore[misc]
    pass
