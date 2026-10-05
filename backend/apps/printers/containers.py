"""DI wiring for printers app."""
from apps.common.container import container
from apps.printers.infrastructure.repositories import (
    DjangoDepartmentRepository,
    DjangoPrinterRepository,
)
from apps.printers.services.printers import DepartmentService, PrinterService


def register_printers() -> None:
    printer_repo = DjangoPrinterRepository()
    dept_repo = DjangoDepartmentRepository()
    container.register("printer_repository", lambda: printer_repo)
    container.register("department_repository", lambda: dept_repo)
    container.register("printer_service", lambda: PrinterService(printer_repo))
    container.register(
        "department_service",
        lambda: DepartmentService(dept_repo),
    )