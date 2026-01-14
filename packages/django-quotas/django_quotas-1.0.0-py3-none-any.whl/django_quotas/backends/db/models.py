#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#

from django_quotas.backends.db.base_models import BaseQuotaUsageModel


class QuotaUsageModel(BaseQuotaUsageModel):
    """Model for tracking quota usage per account, feature, and time point."""

    pass
