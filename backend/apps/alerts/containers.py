"""Alerts DI wiring."""
from apps.alerts.infrastructure.dispatchers import AlertDispatcher
from apps.alerts.infrastructure.repositories import (
    DjangoAlertEventRepository,
    DjangoAlertRuleRepository,
)
from apps.alerts.services.alerts import AlertService
from apps.common.container import container


def register_alerts() -> None:
    rules = DjangoAlertRuleRepository()
    events = DjangoAlertEventRepository()
    dispatcher = AlertDispatcher()
    container.register("alert_rule_repository", lambda: rules)
    container.register("alert_event_repository", lambda: events)
    container.register(
        "alert_service",
        lambda: AlertService(rules, events, dispatcher),
    )