#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

python3 "$REPO_ROOT/developer/tools/generate-test-launcher.py"
echo
echo "Done. You can open developer/test-launcher.html now."
read -n 1 -s -r -p "Press any key to close..."
echo
