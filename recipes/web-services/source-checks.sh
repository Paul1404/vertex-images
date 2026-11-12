#!/usr/bin/env bash
# Validate public CMS recipe sources without production access.
set -euo pipefail
cd "$(dirname "$0")"
bash -n railway-sm-redaxo/entrypoint.sh
for file in railway-*/entrypoint.sh; do
    case "$file" in
        railway-sm-redaxo/entrypoint.sh) ;;
        *) sh -n "$file" ;;
    esac
done
sh -n railway-wengertsberg-wordpress/build-theme-assets.sh
node --test tests/*.test.mjs
node --check railway-wengertsberg-wordpress/theme/site.js
node --check railway-wengertsberg-wordpress/theme/design-preview.js
python3 - <<'PY'
import ast
from pathlib import Path
for path in Path('tests').rglob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
PY
for file in railway-*/analytics/consent.js; do node --check "$file"; done
cmp railway-svu-wordpress/analytics/consent.js railway-wengertsberg-wordpress/analytics/consent.js
cmp railway-svu-wordpress/analytics/consent.js railway-sm-redaxo/analytics/consent.js
cmp railway-svu-wordpress/railway-health.php railway-wengertsberg-wordpress/railway-health.php
