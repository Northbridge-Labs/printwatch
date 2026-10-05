"""Jobs DI container wiring."""
from apps.common.container import container
from apps.jobs.infrastructure.repositories import DjangoJobRepository
from apps.jobs.services.ingestion import JobIngestionFacade, UserResolver


def register_jobs() -> None:
    job_repo = DjangoJobRepository()
    container.register("job_repository", lambda: job_repo)

    def build_facade():
        printer_service = container.resolve("printer_service")
        return JobIngestionFacade(
            job_repo=job_repo,
            printer_service=printer_service,
            user_resolver=UserResolver(),
        )

    container.register("job_ingestion_facade", build_facade)