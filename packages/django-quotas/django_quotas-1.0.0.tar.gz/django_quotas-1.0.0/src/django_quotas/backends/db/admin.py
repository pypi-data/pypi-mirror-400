#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
from django.contrib import admin
from django.http import HttpRequest

from django_quotas.backends.db.models import QuotaUsageModel
from django_quotas.config import DjangoQuotasConfig as cfg


@admin.register(QuotaUsageModel)
class QuotaUsageAdmin(cfg.base_admin_cls()):  # type: ignore[misc]
    readonly_fields = ("account_id", "feature_name", "point_in_time", "usage_count")
    list_display = ("account_id", "feature_name", "point_in_time", "usage_count")
    search_fields = ("account_id",)
    list_filter = ("feature_name", "point_in_time")
    ordering = ("-point_in_time",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
