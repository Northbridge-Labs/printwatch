"""Django management command: ``python manage.py run_consumer``."""
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.ingest.consumer import ZmqConsumer


class Command(BaseCommand):
    help = "Start the ZeroMQ PULL consumer that ingests print job frames."

    def handle(self, *args, **options):
        from django.conf import settings
        consumer = ZmqConsumer(
            bind_host=settings.ZMQ_BIND_HOST,
            ingest_url="http://localhost:8000/api/ingest/jobs",
            service_token=settings.INGEST_SERVICE_TOKEN,
            spool_dir=Path(settings.INGEST_SPOOL_DIR),
        )
        consumer.run_forever()