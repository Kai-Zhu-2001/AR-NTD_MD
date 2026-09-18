#!/usr/bin/env bash
# Run from this simulation directory.
exec bash ../../../scripts/prepare_swish.sh "$PWD" 1 -r npt.gro "$@"
