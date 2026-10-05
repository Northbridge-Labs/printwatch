"""PrintWatch Windows agent.

Tails ``%ProgramData%\\PrintWatch\\jobs.jsonl`` and PUSHes each line to the
backend ZeroMQ endpoint. Registers as a Windows service via ``pywin32``.

Configuration is read from ``%ProgramData%\\PrintWatch\\config.json``::

    {
        "zmq_endpoint": "tcp://backend-host:5558",
        "log_file": "C:\\ProgramData\\PrintWatch\\jobs.jsonl"
    }
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import zmq

DEFAULT_CONFIG = {
    "zmq_endpoint": "tcp://localhost:5558",
    "log_file": os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"),
                             "PrintWatch", "jobs.jsonl"),
    "spool_dir": os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"),
                              "PrintWatch", "spool"),
}


def load_config() -> dict:
    cfg_path = os.path.join(
        os.environ.get("PROGRAMDATA", "C:\\ProgramData"),
        "PrintWatch", "config.json",
    )
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(cfg_path):
        with open(cfg_path) as fh:
            cfg.update(json.load(fh))
    return cfg


class Agent:
    def __init__(self) -> None:
        self.cfg = load_config()
        self._ctx = zmq.Context.instance()
        self._sock = self._ctx.socket(zmq.PUSH)
        self._sock.setsockopt(zmq.LINGER, 500)
        self._sock.connect(self.cfg["zmq_endpoint"])
        os.makedirs(self.cfg["spool_dir"], exist_ok=True)
        self._inode = 0

    def run_forever(self) -> None:
        path = self.cfg["log_file"]
        offset = 0
        while True:
            try:
                if not os.path.exists(path):
                    time.sleep(2)
                    continue
                with open(path, "r", encoding="utf-8") as fh:
                    fh.seek(offset)
                    for line in fh:
                        line = line.strip()
                        if line:
                            self._send(json.loads(line))
                    offset = fh.tell()
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as exc:
                sys.stderr.write(f"[pw-agent] error: {exc}\n")
                time.sleep(2)

    def _send(self, frame: dict) -> None:
        try:
            self._sock.send_json(frame, zmq.NOBLOCK)
        except zmq.Again:
            self._spool(frame)

    def _spool(self, frame: dict) -> None:
        path = Path(self.cfg["spool_dir"]) / f"{time.time_ns()}.json"
        path.write_text(json.dumps(frame))


if __name__ == "__main__":
    Agent().run_forever()