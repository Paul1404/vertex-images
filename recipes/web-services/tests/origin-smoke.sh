#!/bin/bash
set -euo pipefail
image=${1:?image required}
directory=${2:?origin build directory required}
exec python3 "$(dirname "$0")/release-smoke.py" "$directory" "$image"
