#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
import abc
import dataclasses
import datetime
from enum import StrEnum
import uuid

__all__ = [
    "QuotaBucket",
    "ValuePerBucket",
    "QuotaStatus",
    "QuotaStats",
    "QuotaUseForBucket",
    "Quota",
    "QuotaUsage",
]


class QuotaBucket(StrEnum):
    """Enumeration of supported quota buckets."""

    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    TOTAL = "total"


@dataclasses.dataclass(kw_only=True)
class ValuePerBucket:
    """Hold quota values for each bucket type.

    :param hourly: Hourly quota value.
    :param daily: Daily quota value.
    :param monthly: Monthly quota value.
    :param total: Total quota value.
    """

    hourly: int | None = None
    daily: int | None = None
    monthly: int | None = None
    total: int | None = None


@dataclasses.dataclass(kw_only=True)
class QuotaStatus:
    """Represent the status of a quota, including limits and usage.

    :param quota_id: Unique identifier for the quota.
    :param limits: Quota limits per bucket.
    :param usage: Current usage per bucket.
    """

    quota_id: uuid.UUID
    limits: ValuePerBucket
    usage: ValuePerBucket

    def is_exceeded(self) -> bool:
        """Check if any quota limit is exceeded.

        @return: True if any quota is exceeded, False otherwise.
        """
        if self.limits.daily is not None and self.usage.daily is not None and self.usage.daily >= self.limits.daily:
            return True
        if (
            self.limits.monthly is not None
            and self.usage.monthly is not None
            and self.usage.monthly >= self.limits.monthly
        ):
            return True
        if self.limits.total is not None and self.usage.total is not None and self.usage.total >= self.limits.total:
            return True
        return False


@dataclasses.dataclass(kw_only=True)
class QuotaStats:
    """Aggregate quota status for an account and its features.

    :param account_id: Account identifier.
    :param feature_stats: Mapping of feature names to their quota status.
    """

    account_id: str
    feature_stats: dict[str, QuotaStatus]

    def has_exceeded_quotas(self) -> bool:
        """Check if any feature has exceeded quotas.

        @return: True if any feature has exceeded its quota, False otherwise.
        """
        return any(status.is_exceeded() for status in self.feature_stats.values())


@dataclasses.dataclass(kw_only=True)
class QuotaUseForBucket:
    """Usage and limit information for a specific quota bucket.

    :param bucket_name: Name of the quota bucket.
    :param current_usage: Current usage value.
    :param limit: Limit for the bucket.
    :param quota_id: Associated quota identifier.
    """

    bucket_name: QuotaBucket
    current_usage: int
    limit: int | None
    quota_id: uuid.UUID

    @property
    def overuse(self) -> int | None:
        """Return the amount by which the usage exceeds the limit, or None if no limit.

        @return: Overuse amount or None.
        """
        if self.limit is None:
            return None
        return self.current_usage - self.limit


class Quota(metaclass=abc.ABCMeta):
    """Abstract base class for quota definitions."""

    @property
    @abc.abstractmethod
    def id(self) -> uuid.UUID:
        """Return the unique identifier for the quota.

        @return: Quota UUID.
        """
        pass

    @property
    @abc.abstractmethod
    def account_id(self) -> uuid.UUID:
        """Return the account identifier associated with the quota.

        @return: Account UUID.
        """
        pass

    @property
    @abc.abstractmethod
    def feature_name(self) -> str:
        """Return the feature name associated with the quota.

        @return: Feature name string.
        """
        pass

    @property
    @abc.abstractmethod
    def get_limits(self) -> ValuePerBucket:
        """Return the quota limits for each bucket.

        @return: ValuePerBucket instance.
        """
        pass


class QuotaUsage(metaclass=abc.ABCMeta):
    """Abstract base class for quota usage records."""

    @property
    @abc.abstractmethod
    def account_id(self) -> uuid.UUID:
        """Return the account identifier for the usage record.

        @return: Account UUID.
        """
        pass

    @property
    @abc.abstractmethod
    def feature_name(self) -> str:
        """Return the feature name for the usage record.

        @return: Feature name string.
        """
        pass

    @property
    @abc.abstractmethod
    def point_in_time(self) -> datetime.datetime:
        """Return the timestamp of the usage record.

        @return: Datetime of usage.
        """
        pass

    @property
    @abc.abstractmethod
    def usage_count(self) -> int:
        """Return the usage count for the record.

        @return: Usage count as integer.
        """
        pass
