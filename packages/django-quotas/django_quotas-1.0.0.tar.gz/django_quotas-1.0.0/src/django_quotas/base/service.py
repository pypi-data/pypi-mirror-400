#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
import abc
from collections import defaultdict
import uuid

from asgiref.sync import sync_to_async

from django_quotas.base.dto import Quota, QuotaBucket, QuotaStats, QuotaUseForBucket, ValuePerBucket

__all__ = [
    "QuotaExceededError",
    "QuotaService",
]

from django_quotas.base.features import FeatureId


class QuotaExceededError(Exception):
    """Exception raised when a quota is exceeded for an account and feature(s).

    :param account_name: The account UUID.
    :param exceeded_features: Mapping of feature names to exceeded bucket stats.
    """

    def __init__(self, account_name: str, exceeded_features: dict[str, list[QuotaUseForBucket]]):
        self.account_id = account_name
        self._exceeded_features_stats = exceeded_features
        super().__init__(self.__generate_detailed_message())

    def get_exceeded_features(self) -> set[str]:
        """Get the set of feature names for which quotas are exceeded.

        :return: Set of feature names.
        """
        return set(self._exceeded_features_stats.keys())

    def get_stats_per_feature(self) -> dict[str, list[QuotaUseForBucket]]:
        """Get the exceeded stats per feature.

        :return: Mapping of feature names to list of QuotaUseForBucket.
        """
        return self._exceeded_features_stats

    def __generate_detailed_message(self) -> str:
        msg = self.__generate_msg() + "\nDetails:"
        for feature, stats in self._exceeded_features_stats.items():
            msg += f"\n{feature}: "
            buckets = []
            for stat in stats:
                buckets.append(f"{stat.bucket_name}({stat.current_usage}/{stat.limit})")
            msg += ", ".join(buckets)
        return msg

    def __generate_msg(self) -> str:
        return f"Quota exceeded for account {self.account_id}. Exceeded features: {self.get_exceeded_features()}"


class QuotaService(metaclass=abc.ABCMeta):
    """Abstract base class for quota service implementations."""

    def ensure_quota_or_raise(
        self, account_id: str, feature: FeatureId | set[FeatureId], potential_increase: int = 1
    ) -> None:
        """
        Ensure that the quota for the given account and feature is not exceeded.

        If the quota is exceeded, raise a QuotaExceededError.
        :param account_id: The account ID.
        :param feature: The feature name or set of feature names.
        :param potential_increase: The potential increase in usage.\
            Current utilization + potential increase must be less than the quota.
        :raise QuotaExceededError: If the quota is exceeded.
        """
        feature_names: set[str] = self.resolve_feature_names(feature)
        utilization = self.get_quotas_utilization(account_id, feature)
        exceeded_features: dict[str, list[QuotaUseForBucket]] = defaultdict(list)
        for feature in feature_names:
            if feature not in utilization.feature_stats:
                continue  # this means we have no quota for this specific feature
            status = utilization.feature_stats[feature]
            quota_buckets = [
                (QuotaBucket.HOURLY, status.usage.hourly or 0, status.limits.hourly),
                (QuotaBucket.DAILY, status.usage.daily or 0, status.limits.daily),
                (QuotaBucket.MONTHLY, status.usage.monthly or 0, status.limits.monthly),
                (QuotaBucket.TOTAL, status.usage.total or 0, status.limits.total),
            ]

            for bucket_name, current_usage, limit in quota_buckets:
                if limit is not None and current_usage + potential_increase > limit:
                    exceeded_features[feature].append(
                        QuotaUseForBucket(
                            bucket_name=bucket_name,
                            current_usage=current_usage,
                            limit=limit,
                            quota_id=status.quota_id,
                        )
                    )
        if exceeded_features:
            raise QuotaExceededError(account_id, exceeded_features)

    async def aensure_quota_or_raise(
        self, account_id: str, feature: FeatureId | set[FeatureId], potential_increase: int = 1
    ) -> None:
        """
        Ensure that the quota for the given account and feature is not exceeded.

        If the quota is exceeded, raise a QuotaExceededError.
        :param account_id: The account ID.
        :param feature: The feature name.
        :param potential_increase: The potential increase in usage.\
            Current utilization + potential_increase must be less than the quota.
        """
        return await sync_to_async(self.ensure_quota_or_raise)(account_id, feature, potential_increase)

    @abc.abstractmethod
    def register_usage(self, account_id: str, feature: FeatureId, increment: int = 1) -> None:
        """
        Register usage for the given account and feature.

        :param account_id: The account ID.
        :param feature: The feature name.
        :param increment: The value to be added to quota usage.
        """
        pass

    @abc.abstractmethod
    async def aregister_usage(self, account_id: str, feature: FeatureId | set[FeatureId], increment: int = 1) -> None:
        """
        Register usage for the given account and feature.

        :param account_id: The account ID.
        :param feature: The feature name.
        :param increment: The value to be added to quota usage.
        """
        pass

    @abc.abstractmethod
    def get_quotas_utilization(self, account_id: str, feature: FeatureId | set[FeatureId] | None) -> QuotaStats:
        """
        Get the quota utilization for the given account and features.

        :param account_id: The account ID.
        :param feature: Name of the feature or a list of feature names. None means all features having quotas.
        """
        pass

    def _get_account_id_for_quota_search(self, account_id: str) -> str:
        """
        Get the account ID to be used for quota search.
        This method can be overridden in subclasses to modify the account ID e.g. if for anonymous users account ID
        is generated dynamically e.g. based on IP address or session ID you most likely want to setup quota for ANY
        anonymous user rather than for each unique anonymous user. So this is the right place to transform account ID
        into a common one for all anonymous users.

        :param account_id: The account ID.
        :return: The account ID to be used for quota search.
        """
        return account_id

    @abc.abstractmethod
    async def aget_quotas_utilization(self, account_id: str, feature: FeatureId | set[FeatureId] | None) -> QuotaStats:
        """
        Get the quota utilization for the given account and features.

        :param account_id: The account ID.
        :param feature: Name of the feature or a list of feature names. None means all features having quotas.
        """
        pass

    @abc.abstractmethod
    def set_quota(
        self, account_id: str, feature: FeatureId, limits: ValuePerBucket, owner_tag: str | None = None
    ) -> Quota:
        """
        Set the quota for the given account and feature.

        :param account_id: The account ID.
        :param feature: The feature name.
        :param limits: Limits for each bucket.
        :param owner_tag: Optional owner tag.
        :return: The created or updated quota.
        """
        pass

    @abc.abstractmethod
    async def aset_quota(
        self, account_id: str, feature: FeatureId, limits: ValuePerBucket, owner_tag: str | None = None
    ) -> Quota:
        """
        Set the quota for the given account and feature.

        :param account_id: The account ID.
        :param feature: The feature name.
        :param limits: Limits for each bucket.
        :param owner_tag: Optional owner tag.
        :return: The created or updated quota.
        """
        pass

    @staticmethod
    def resolve_feature_names(features: FeatureId | set[FeatureId]) -> set[str]:
        """
        Resolve feature names from FeatureId or set of FeatureId.

        :param features: FeatureId or set of FeatureId.
        :return: Set of feature names.
        """
        if isinstance(features, set):
            return {QuotaService.resolve_feature_name(f) for f in features}
        return {QuotaService.resolve_feature_name(features)}

    @staticmethod
    def resolve_feature_name(feature: FeatureId) -> str:
        """
        Resolve feature name from FeatureId.

        :param feature: FeatureId.
        :return: Feature name.
        """
        if isinstance(feature, str):
            return feature
        return feature.full_name
