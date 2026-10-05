"""Unit tests for the cost calculation strategy (no Django needed)."""
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from apps.jobs.domain.records import JobRecord
from apps.jobs.services.cost import (
    CopyCostStrategy,
    CostStrategyFactory,
    PrintCostStrategy,
    ScanCostStrategy,
)


def _printer(bw="0.10", color="0.50", scan="0.05"):
    return SimpleNamespace(
        cost_per_page_bw=Decimal(bw),
        cost_per_page_color=Decimal(color),
        scan_cost_per_page=Decimal(scan),
    )


def _record(job_type="print", pages=10, copies=1, color=False):
    return JobRecord(
        job_type=job_type, source="api", printer_name="HP",
        username="jdoe", document_name="doc", pages=pages, copies=copies,
        color=color, duplex=False, submitted_at=datetime(2026, 1, 1),
        raw_payload={},
    )


def test_print_cost_bw():
    job = _record("print", pages=10, copies=2, color=False)
    cost = PrintCostStrategy().cost(job, _printer())
    assert cost == Decimal("2.00")  # 10 * 2 * 0.10


def test_print_cost_color():
    job = _record("print", pages=10, copies=1, color=True)
    cost = PrintCostStrategy().cost(job, _printer())
    assert cost == Decimal("5.00")  # 10 * 1 * 0.50


def test_copy_cost_matches_print():
    job = _record("copy", pages=4, copies=3, color=False)
    assert CopyCostStrategy().cost(job, _printer()) == Decimal("1.20")


def test_scan_cost_uses_scan_rate():
    job = _record("scan", pages=8)
    assert ScanCostStrategy().cost(job, _printer()) == Decimal("0.40")


def test_factory_resolves_strategy_by_type():
    assert isinstance(CostStrategyFactory.get("print"), PrintCostStrategy)
    assert isinstance(CostStrategyFactory.get("scan"), ScanCostStrategy)
    assert isinstance(CostStrategyFactory.get("copy"), CopyCostStrategy)


def test_factory_raises_on_unknown_type():
    import pytest
    with pytest.raises(ValueError):
        CostStrategyFactory.get("fax")


def test_factory_register_extends_strategies():
    class FaxStrategy(PrintCostStrategy):
        pass
    CostStrategyFactory.register("fax", FaxStrategy())
    assert isinstance(CostStrategyFactory.get("fax"), FaxStrategy)


def test_cost_with_no_printer_returns_zero():
    job = _record("print", pages=10)
    assert PrintCostStrategy().cost(job, None) == Decimal(0)