"""JobIngestionFacade: single entry point used by REST + zmq-consumer.

Responsibilities (orchestration only; business logic lives in services):
1. Resolve the printer (auto-create if unknown, optional via setting).
2. Resolve the user by username (case-insensitive).
3. Compute cost via the Strategy (CostStrategyFactory).
4. Persist via the repository.
5. Run the post-ingest pipeline (quota + alert) via Chain of Responsibility.
"""
from __future__ import annotations

from typing import Optional

from apps.jobs.domain.interfaces import (
    IJobIngestionFacade,
    IJobRepository,
)
from apps.jobs.domain.records import IngestResult, JobRecord
from apps.jobs.services.cost import CostStrategyFactory
from apps.jobs.services.pipeline import PipelineContext, build_default_pipeline


class JobIngestionFacade(IJobIngestionFacade):
    def __init__(
        self,
        job_repo: IJobRepository,
        printer_service,
        user_resolver,
        pipeline=None,
    ) -> None:
        self._job_repo = job_repo
        self._printer_service = printer_service
        self._user_resolver = user_resolver
        self._pipeline = pipeline or build_default_pipeline()

    def ingest(self, record: JobRecord) -> IngestResult:
        # 1. Resolve printer
        printer = self._printer_service.get_or_create_by_name(record.printer_name)

        # 2. Resolve user
        user_id = self._user_resolver.resolve(record.username)
        flags: list = []
        if user_id is None:
            flags.append("unmatched_user")

        # 3. Cost
        strategy = CostStrategyFactory.get(record.job_type)
        cost = strategy.cost(record, printer)

        # 4. Persist
        persisted = self._job_repo.save(
            record,
            printer_id=printer.id if printer else None,
            user_id=user_id,
            cost=cost,
            flags=flags,
        )

        # 5. Pipeline
        result = IngestResult(job=persisted)
        ctx = PipelineContext(job=persisted, result=result)
        self._pipeline.handle(ctx)
        return result


class UserResolver:
    """Resolves a raw username to a Django user id (case-insensitive)."""

    def __init__(self) -> None:
        from apps.accounts.infrastructure.models import User
        self._User = User

    def resolve(self, username: str) -> Optional[int]:
        if not username:
            return None
        try:
            user = self._User.objects.get(username__iexact=username)
        except self._User.DoesNotExist:
            # Try email
            try:
                user = self._User.objects.get(email__iexact=username)
            except self._User.DoesNotExist:
                return None
        return user.id