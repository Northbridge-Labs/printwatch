# PrintWatch CUPS filter

A Python CUPS filter that captures print job metadata (user, pages, copies,
printer) and forwards it over ZeroMQ (PUSH) to the PrintWatch backend's
`zmq-consumer` daemon.

## How it works

CUPS invokes filters as:

    pwfilter job-id user title copies options [file]

The filter:

1. Reads the spool file (or stdin) — counts pages via `pypdf` when possible.
2. Builds a JSON frame with `source=cups` and the captured metadata.
3. PUSHes the frame to the endpoint in `PW_ZMQ_ENDPOINT`
   (default `tcp://localhost:5558`).
4. Writes the original data unchanged to stdout so the rest of the CUPS
   filter chain runs normally.

A send failure is logged but does **not** fail the print job — the spooler
never sees an error from the logging side.

## Installation

```bash
sudo ./install.sh
```

Then enable the filter on a queue (driverless / IPP Everywhere queues use
filter chains, not PPDs):

```bash
sudo lpadmin -p myqueue -o cupsFilter='application/vnd.cups-pdf:pwfilter'
```

See the CUPS documentation for `cupsFilter` and `cupsFilter2` chain syntax.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `PRINTER` / `PRINTER_NAME` | `unknown` | Printer name (set by CUPS) |
| `PW_ZMQ_ENDPOINT` | `tcp://localhost:5558` | ZeroMQ PUSH endpoint |

## Testing manually

```bash
echo "hello" | PW_ZMQ_ENDPOINT=tcp://localhost:5558 \
    PRINTER=TestPrinter ./pw_filter.py 42 jdoe report.pdf 1 "Duplex" -
```