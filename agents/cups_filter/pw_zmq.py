"""ZeroMQ PUSH helper used by the CUPS filter.

Kept dependency-light so it can run in the constrained CUPS filter
environment.
"""
from __future__ import annotations

import json
import os
import socket
import sys

try:
    import zmq  # type: ignore
    _HAS_ZMQ = True
except ImportError:
    _HAS_ZMQ = False


def send(frame: dict) -> bool:
    """PUSH a JSON frame to the configured backend endpoint.

    Returns True on success, False on failure. Never raises — a failed send
    must not interrupt the CUPS filter chain (the spooler would treat the
    job as failed).
    """
    endpoint = os.environ.get("PW_ZMQ_ENDPOINT", "tcp://localhost:5558")
    payload = json.dumps(frame).encode()

    if _HAS_ZMQ:
        try:
            ctx = zmq.Context.instance()
            sock = ctx.socket(zmq.PUSH)
            sock.setsockopt(zmq.LINGER, 500)
            sock.connect(endpoint)
            sock.send(payload, zmq.NOBLOCK)
            sock.close()
            return True
        except Exception as exc:
            sys.stderr.write(f"[pwfilter] zmq send failed: {exc}\n")
            return False

    # Fallback: raw TCP (the consumer is configured to also accept raw JSON
    # lines when ZMQ is unavailable). Disabled by default.
    sys.stderr.write("[pwfilter] pyzmq not installed, skipping send\n")
    return False