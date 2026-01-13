#!/usr/bin/env bash
. .venv/bin/activate
ruff format src \
  && ruff check --select I --fix src \
  && ruff check src \
  && mypy src
if [[ $? -ne 0 ]]; then
  echo "LINT FAILED. CORRECT ERRORS & RE-RUN." >&2
  exit 1
fi
