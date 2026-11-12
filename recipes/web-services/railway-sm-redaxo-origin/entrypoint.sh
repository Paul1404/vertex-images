#!/bin/sh
set -eu

: "${ORIGIN_VERIFY:?missing CloudFront origin verification token}"
: "${REDAXO_UPSTREAM:?missing private REDAXO upstream}"

exec "$@"
