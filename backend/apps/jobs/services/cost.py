"""Cost calculation strategies (Strategy pattern, one per job_type)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from apps.jobs.domain.records import JobRecord


class CostStrategy(ABC):
    """Abstract strategy interface."""

    @abstractmethod
    def cost(self, job: JobRecord, printer) -> Decimal: ...


class PrintCostStrategy(CostStrategy):
    def cost(self, job: JobRecord, printer) -> Decimal:
        if printer is None:
            return Decimal(0)
        rate = printer.cost_per_page_color if job.color else printer.cost_per_page_bw
        return Decimal(rate) * Decimal(job.pages) * Decimal(job.copies)


class CopyCostStrategy(CostStrategy):
    """Same cost model as print (paper consumed)."""

    def cost(self, job: JobRecord, printer) -> Decimal:
        return PrintCostStrategy().cost(job, printer)


class ScanCostStrategy(CostStrategy):
    def cost(self, job: JobRecord, printer) -> Decimal:
        if printer is None:
            return Decimal(0)
        return Decimal(printer.scan_cost_per_page) * Decimal(job.pages)


class CostStrategyFactory:
    """Resolves the right strategy by job_type (Factory pattern)."""

    _strategies: dict[str, CostStrategy] = {
        "print": PrintCostStrategy(),
        "copy": CopyCostStrategy(),
        "scan": ScanCostStrategy(),
    }

    @classmethod
    def get(cls, job_type: str) -> CostStrategy:
        strategy = cls._strategies.get(job_type)
        if strategy is None:
            raise ValueError(f"Unknown job_type: {job_type}")
        return strategy

    @classmethod
    def register(cls, job_type: str, strategy: CostStrategy) -> None:
        """Allow new strategies to be added without modifying this class (OCP)."""
        cls._strategies[job_type] = strategy