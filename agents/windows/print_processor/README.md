# PrintWatch Windows Print Processor

A native Windows print processor DLL that captures print job metadata and
writes it as JSON lines to `%ProgramData%\PrintWatch\jobs.jsonl`. A separate
Python service (`agent/`) tails that file and forwards entries to the
PrintWatch backend over ZeroMQ.

## Why a DLL + Python agent?

Python cannot run inside the Windows spooler (`spoolsv.exe`) — only a native
DLL loaded by the spooler can hook `PrintJob`. So the DLL writes a log file,
and a Python Windows service tails it and handles the network I/O. This keeps
the native part minimal (no HTTP/zmq inside the spooler) and the maintenance
burden in Python.

## Build (Visual Studio 2022, x64)

1. Open a new "Windows Desktop DLL" project targeting x64.
2. Add `PrintProcessor.cpp` and the Windows Print Spooler import library
   (`winspool.lib`).
3. Export the standard print processor entry points
   (`PrintDocumentOnPrinterProcessor`, `OpenPrintProcessor`, etc.).
4. Build to `PrintWatchPrintProcessor.dll`.

See the Microsoft docs for the exact entry points:
https://learn.microsoft.com/en-us/windows-hardware/drivers/print/print-processor-interfaces

## Register

```reg
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Print\Environments\Windows x64\Print Processors\PrintWatch]
    "Driver"="PrintWatchPrintProcessor.dll"
```

Restart the spooler: `Restart-Service Spooler`.

Assign to a printer via PowerShell:

```powershell
Set-Printer -Name "HP-LJ" -PrintProcessor "PrintWatch"
```

## Log file format

`%ProgramData%\PrintWatch\jobs.jsonl` — one JSON object per line:

```json
{"source":"windows","printer":"HP-LJ","username":"DOMAIN\\jdoe","document":"report.pdf","pages":12,"copies":1,"color":false,"duplex":true,"submitted_at":"2026-07-27T10:00:00Z"}
```

The Python agent reads this file and PUSHes each line to the backend.