"""Printers domain records."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class DepartmentRecord:
    id: int
    name: str
    description: str


@dataclass(frozen=True)
class PrinterRecord:
    id: int
    name: str
    host: str
    model: str
    status: str
    department_id: Optional[int]
    cost_per_page_bw: Decimal
    cost_per_page_color: Decimal
    scan_cost_per_page: Decimal