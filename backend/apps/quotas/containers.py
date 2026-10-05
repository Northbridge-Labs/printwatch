"""Quotas DI wiring."""
from apps.common.container import container
from apps.quotas.infrastructure.aggregators import DjangoJobsAggregator
from apps.quotas.infrastructure.repositories import (
    DjangoQuotaRuleRepository,
    DjangoQuotaUsageRepository,
)
from apps.quotas.services.quotas import QuotaService


def register_quotas() -> None:
    rules = DjangoQuotaRuleRepository()
    usages = DjangoQuotaUsageRepository()
    aggregator = DjangoJobsAggregator()
    container.register("quota_rule_repository", lambda: rules)
    container.register("quota_usage_repository", lambda: usages)
    container.register(
        "quota_service",
        lambda: QuotaService(rules, usages, aggregator),
    )