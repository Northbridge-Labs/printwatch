"""Register the PrintWatch agent as a Windows service.

Run as Administrator::

    python install_service.py install
    python install_service.py start

To remove::

    python install_service.py stop
    python install_service.py remove
"""
import sys

import servicemanager  # type: ignore
from win32event import (  # type: ignore
    SERVICE_AUTO_START,
    SERVICE_CLASS_WIN32_OWN_PROCESS,
)
from win32serviceutil import (  # type: ignore
    ServiceHandle,
    HandleCommandLine,
    InstallService,
)


class PrintWatchAgentService:
    _svc_name_ = "PrintWatchAgent"
    _svc_display_name_ = "PrintWatch Agent"
    _svc_description_ = (
        "Tails %ProgramData%\\PrintWatch\\jobs.jsonl and forwards job "
        "metadata to the PrintWatch backend over ZeroMQ."
    )

    def SvcDoRun(self):  # noqa: N802
        from pw_agent import Agent
        Agent().run_forever()

    def SvcStop(self):  # noqa: N802
        pass


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle()
        servicemanager.StartServiceCtrlDispatcher()
    else:
        HandleCommandLine(PrintWatchAgentService)