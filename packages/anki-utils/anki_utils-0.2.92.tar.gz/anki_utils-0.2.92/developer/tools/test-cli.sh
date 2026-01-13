#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 -m pip install -e "$REPO_ROOT"

python3 -m anki_utils.cli themes --list
python3 -m anki_utils.cli themes --get minimal
python3 -m anki_utils.cli asset preview-template > /dev/null
echo '{"cards":[]}' | python3 -m anki_utils.cli export-apkg --output "$REPO_ROOT/test.apkg"
rm -f "$REPO_ROOT/test.apkg"
