"""Printers service: business logic over repository interfaces."""
from __future__ import annotations

from apps.printers.domain.interfaces import (
    IDepartmentRepository, IPrinterRepository,
)
from apps.printers.domain.records import DepartmentRecord, PrinterRecord


class PrinterService:
    def __init__(self, printers: IPrinterRepository) -> None:
        self._printers = printers

    def list(self) -> list[PrinterRecord]:
        return self._printers.list_all()

    def get(self, printer_id: int):
        return self._printers.get_by_id(printer_id)

    def get_or_create_by_name(self, name: str):
        existing = self._printers.get_by_name(name)
        if existing is not None:
            return existing
        return self._printers.create({
            "name": name, "host": "", "model": "", "status": "unknown",
        })

    def create(self, data: dict) -> PrinterRecord:
        return self._printers.create(data)

    def update(self, printer_id: int, data: dict):
        return self._printers.update(printer_id, data)

    def delete(self, printer_id: int) -> bool:
        return self._printers.delete(printer_id)


class DepartmentService:
    def __init__(self, departments: IDepartmentRepository) -> None:
        self._departments = departments

    def list(self) -> list[DepartmentRecord]:
        return self._departments.list_all()

    def get(self, department_id: int):
        return self._departments.get_by_id(department_id)

    def create(self, name: str, description: str = "") -> DepartmentRecord:
        return self._departments.create(name, description)

    def update(self, department_id: int, name: str, description: str):
        return self._departments.update(department_id, name, description)

    def delete(self, department_id: int) -> bool:
        return self._departments.delete(department_id)