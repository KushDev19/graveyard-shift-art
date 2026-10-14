#!/bin/sh
# full rebuild of one room: masks -> objects -> shell+lights(+mist) -> composite -> per-object checks
set -e
cd "$(dirname "$0")"
python3 masks.py "$1"
python3 build.py "$1" objects
python3 build.py "$1" shell
python3 build.py "$1" compose
python3 build.py "$1" check
