"""Reporting DI wiring."""
from apps.common.container import container
from apps.reporting.services.reporting import ReportingService


def register_reporting() -> None:
    container.register("reporting_service", lambda: ReportingService())