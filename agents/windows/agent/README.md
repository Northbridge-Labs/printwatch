# PrintWatch Windows Agent

Python Windows service that tails the JSONL log written by the native
print processor DLL and forwards each job entry to the PrintWatch backend
over ZeroMQ (PUSH).

## Setup

```powershell
pip install -r requirements.txt
python install_service.py install
python install_service.py start
```

## Configuration

Edit `C:\ProgramData\PrintWatch\config.json` (create the folder if missing):

```json
{
    "zmq_endpoint": "tcp://backend-host:5558",
    "log_file": "C:\\ProgramData\\PrintWatch\\jobs.jsonl"
}
```

## Bundling

To distribute without a Python install:

```powershell
pyinstaller --onefile --service pw_agent.py
```

## Log rotation

The agent tracks the file by byte offset; if the print processor rotates
the log, the agent picks up the new file automatically on the next poll
cycle.