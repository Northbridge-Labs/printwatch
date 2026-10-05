"""Printers repositories."""
from __future__ import annotations

from typing import Optional

from .models import Department, Printer
from apps.printers.domain.records import DepartmentRecord, PrinterRecord


def _to_printer(p: Printer) -> PrinterRecord:
    return PrinterRecord(
        id=p.id, name=p.name, host=p.host, model=p.model, status=p.status,
        department_id=p.department_id,
        cost_per_page_bw=p.cost_per_page_bw,
        cost_per_page_color=p.cost_per_page_color,
        scan_cost_per_page=p.scan_cost_per_page,
    )


def _to_department(d: Department) -> DepartmentRecord:
    return DepartmentRecord(id=d.id, name=d.name, description=d.description)


class DjangoPrinterRepository:
    def get_by_name(self, name: str) -> Optional[PrinterRecord]:
        try:
            return _to_printer(Printer.objects.get(name=name))
        except Printer.DoesNotExist:
            return None

    def get_by_id(self, printer_id: int) -> Optional[PrinterRecord]:
        try:
            return _to_printer(Printer.objects.get(id=printer_id))
        except Printer.DoesNotExist:
            return None

    def list_all(self) -> list[PrinterRecord]:
        return [_to_printer(p) for p in Printer.objects.all()]

    def create(self, data: dict) -> PrinterRecord:
        p = Printer.objects.create(**data)
        return _to_printer(p)

    def update(self, printer_id: int, data: dict) -> Optional[PrinterRecord]:
        try:
            p = Printer.objects.get(id=printer_id)
        except Printer.DoesNotExist:
            return None
        for k, v in data.items():
            setattr(p, k, v)
        p.save()
        return _to_printer(p)

    def delete(self, printer_id: int) -> bool:
        deleted, _ = Printer.objects.filter(id=printer_id).delete()
        return bool(deleted)


class DjangoDepartmentRepository:
    def get_by_id(self, department_id: int) -> Optional[DepartmentRecord]:
        try:
            return _to_department(Department.objects.get(id=department_id))
        except Department.DoesNotExist:
            return None

    def list_all(self) -> list[DepartmentRecord]:
        return [_to_department(d) for d in Department.objects.all()]

    def create(self, name: str, description: str = "") -> DepartmentRecord:
        d = Department.objects.create(name=name, description=description)
        return _to_department(d)

    def update(self, department_id: int, name: str, description: str) -> Optional[DepartmentRecord]:
        try:
            d = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return None
        d.name = name
        d.description = description
        d.save()
        return _to_department(d)

    def delete(self, department_id: int) -> bool:
        deleted, _ = Department.objects.filter(id=department_id).delete()
        return bool(deleted)