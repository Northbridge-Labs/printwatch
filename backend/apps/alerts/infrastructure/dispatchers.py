"""Alert dispatchers: send notifications via email or webhook."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class AlertDispatcher:
    def send(self, rule, event) -> None:
        if rule.channel == "email":
            self._send_email(rule, event)
        elif rule.channel == "webhook":
            self._send_webhook(rule, event)
        from apps.alerts.infrastructure.repositories import (
            DjangoAlertEventRepository,
        )
        DjangoAlertEventRepository().mark_sent(event.id)

    def _send_email(self, rule, event) -> None:
        logger.info("ALERT EMAIL -> %s: %s", rule.target or rule.name, event.message)
        # In production: integrate with django.core.mail.send_mail

    def _send_webhook(self, rule, event) -> None:
        import json
        import urllib.request
        if not rule.target:
            return
        payload = json.dumps({
            "rule": rule.name, "message": event.message, "event_id": event.id,
        }).encode()
        try:
            req = urllib.request.Request(
                rule.target, data=payload,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as exc:
            logger.warning("Webhook dispatch failed: %s", exc)