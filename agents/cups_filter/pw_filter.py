#!/usr/bin/env python3
"""PrintWatch CUPS filter.

Invoked by CUPS as::

    pwfilter job-id user title copies options [file]

Reads the spool file (if any) and forwards a JSON frame describing the job
to the PrintWatch backend via ZeroMQ (PUSH). The filter is a passthrough:
the original data is copied from stdin (or ``file``) to stdout so the rest
of the CUPS filter chain is unaffected.

Environment variables:
    PRINTER / PRINTER_NAME  printer name (provided by CUPS)
    PW_ZMQ_ENDPOINT         ZeroMQ endpoint (default tcp://localhost:5558)

Install with ``install.sh`` and add to the target queues' filter chain.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

from pw_zmq import send as zmq_send


def _page_count(argv_file: str | None) -> int:
    """Best-effort page count from the spool file."""
    if not argv_file or not os.path.exists(argv_file):
        return 0
    try:
        from pypdf import PdfReader
        reader = PdfReader(argv_file)
        return len(reader.pages)
    except Exception:
        return 0


def _printer_name() -> str:
    return os.environ.get("PRINTER") or os.environ.get("PRINTER_NAME") or "unknown"


def main(argv: list[str]) -> int:
    if len(argv) < 6:
        sys.stderr.write("[pwfilter] usage: pwfilter job-id user title copies options [file]\n")
        return 1

    job_id, user, title, copies_str, options = argv[1:6]
    argv_file = argv[6] if len(argv) > 6 else None
    copies = int(copies_str or 1)

    # Read stdin if no file arg (CUPS pipe mode)
    data = b""
    if argv_file and os.path.exists(argv_file):
        with open(argv_file, "rb") as fh:
            data = fh.read()
    else:
        try:
            data = sys.stdin.buffer.read()
        except Exception:
            data = b""

    pages = _page_count(argv_file)

    frame = {
        "v": 1,
        "source": "cups",
        "printer": _printer_name(),
        "username": user,
        "document": title,
        "pages": pages,
        "copies": copies,
        "color": False,
        "duplex": "Duplex" in options,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "raw": {"cups_job_id": job_id, "cups_options": options},
    }

    try:
        zmq_send(frame)
    except Exception as exc:
        sys.stderr.write(f"[pwfilter] send error: {exc}\n")

    # Passthrough: write the original data to stdout for the next filter.
    if data:
        sys.stdout.buffer.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))