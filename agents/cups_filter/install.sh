#!/bin/bash
# Install the PrintWatch CUPS filter.
# Usage: sudo ./install.sh
set -e

FILTER_NAME="pwfilter"
FILTER_SRC="$(dirname "$0")/pw_filter.py"
FILTER_DST="/usr/lib/cups/filter/${FILTER_NAME}"
ZMQ_HELPER="$(dirname "$0")/pw_zmq.py"
ZMQ_DST="/usr/lib/cups/filter/pw_zmq.py"

if [ "$(id -u)" -ne 0 ]; then
    echo "Run with sudo." >&2
    exit 1
fi

echo "Installing ${FILTER_NAME} to ${FILTER_DST}"
install -m 0755 -o root -g root "${FILTER_SRC}" "${FILTER_DST}"
install -m 0644 -o root -g root "${ZMQ_HELPER}" "${ZMQ_DST}"

# Install pyzmq for the system python used by CUPS (best effort)
python3 -m pip install --quiet pyzmq pypdf || true

echo
echo "Filter installed. To activate it on a queue, use lpadmin:"
echo
echo "  sudo lpadmin -p <queue-name> -o cupsFilter='application/vnd.cups-pdf:pwfilter'"
echo
echo "Or prepend it to the filter chain via the PPD/Driverless policy. See README.md."