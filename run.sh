#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

usage() {
    cat <<'EOF'
Usage: ./run.sh [--skip-tests]

Checks that Python and gpiozero are available, then starts main.py.
Use --skip-tests to start without running the unit tests first.
EOF
}

run_tests=true
case "${1:-}" in
    "") ;;
    --skip-tests) run_tests=false ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
esac

cd "$ROOT_DIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Error: Python executable '$PYTHON_BIN' was not found." >&2
    exit 1
fi

echo "Checking Python source..."
"$PYTHON_BIN" -m compileall -q .

if "$run_tests"; then
    echo "Running unit tests..."
    "$PYTHON_BIN" -m pytest -q
fi

echo "Checking gpiozero library..."
"$PYTHON_BIN" - <<'PY'

try:
    import gpiozero
except ImportError as error:
    raise SystemExit(
        "Error: gpiozero is not installed. Install it with: "
        "python3 -m pip install gpiozero lgpio"
    ) from error

print(f"gpiozero {gpiozero.__version__} is available.")
PY

echo "Starting controller. Press Ctrl-C to stop safely."

exec "$PYTHON_BIN" main.py