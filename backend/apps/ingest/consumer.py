"""ZeroMQ consumer daemon: pulls job frames and POSTs to internal ingest API.

Implements the Adapter pattern: translates wire JSON into the same payload
accepted by ``/api/ingest/jobs/``, with on-disk spooling for resilience.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

import requests
import zmq

logger = logging.getLogger("ingest")


class ZmqConsumer:
    """PULL socket bound on ``ZMQ_BIND_HOST``, forwards to DRF ingest endpoint."""

    def __init__(
        self,
        bind_host: str,
        ingest_url: str,
        service_token: str,
        spool_dir: Path,
    ) -> None:
        self._bind_host = bind_host
        self._ingest_url = ingest_url
        self._service_token = service_token
        self._spool_dir = spool_dir
        self._spool_dir.mkdir(parents=True, exist_ok=True)
        self._context: Optional[zmq.Context] = None
        self._socket: Optional[zmq.Socket] = None

    def run_forever(self) -> None:
        self._context = zmq.Context.instance()
        self._socket = self._context.socket(zmq.PULL)
        self._socket.bind(self._bind_host)
        logger.info("ZmqConsumer bound on %s", self._bind_host)
        # Re-flush any spooled frames from previous run
        self._replay_spool()
        while True:
            try:
                frame = self._socket.recv_json()
                self._handle(frame)
            except KeyboardInterrupt:
                logger.info("Shutting down ZmqConsumer")
                break
            except Exception as exc:
                logger.exception("Consumer error: %s", exc)
                time.sleep(1)

    def _handle(self, frame: dict) -> None:
        ok = self._post(frame)
        if not ok:
            self._spool(frame)

    def _post(self, frame: dict) -> bool:
        try:
            resp = requests.post(
                self._ingest_url,
                json=frame,
                headers={"X-Ingest-Token": self._service_token},
                timeout=5,
            )
            return resp.status_code in (200, 201)
        except Exception as exc:
            logger.warning("POST ingest failed: %s", exc)
            return False

    def _spool(self, frame: dict) -> None:
        path = self._spool_dir / f"{time.time_ns()}.json"
        path.write_text(json.dumps(frame))
        logger.info("Spooled frame to %s", path)

    def _replay_spool(self) -> None:
        for path in sorted(self._spool_dir.glob("*.json")):
            try:
                frame = json.loads(path.read_text())
            except Exception:
                path.unlink(missing_ok=True)
                continue
            if self._post(frame):
                path.unlink(missing_ok=True)
                logger.info("Replayed spooled frame %s", path)