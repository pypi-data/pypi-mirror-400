#!/bin/bash

set -e

cd "$(dirname "$(readlink -f "$0")")"

# prevents harmless 'VIRTUAL_ENV=XXX does not match the project environment path'
# when running this file from a different dir
unset VIRTUAL_ENV

uv run pytest -v -s --no-cov test "$@"
