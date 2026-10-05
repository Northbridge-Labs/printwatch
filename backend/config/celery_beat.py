"""Celery beat schedule (registered via Django settings CELERY_BEAT_SCHEDULE)."""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "recompute-all-quotas": {
        "task": "apps.quotas.tasks.recompute_all_quotas",
        "schedule": crontab(minute="*/10"),
    },
    "check-printer-status": {
        "task": "apps.alerts.tasks.check_printer_status",
        "schedule": crontab(minute="*/5"),
    },
}