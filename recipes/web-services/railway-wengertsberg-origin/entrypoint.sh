#!/bin/sh
set -eu

: "${ORIGIN_VERIFY:?missing CloudFront origin verification token}"
: "${WORDPRESS_UPSTREAM:?missing private WordPress upstream}"

exec "$@"
