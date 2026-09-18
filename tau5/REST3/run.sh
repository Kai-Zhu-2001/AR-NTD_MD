#!/usr/bin/env bash

# Submit or run from this simulation directory.
exec bash ../../scripts/run_replicas.sh rest3 "$PWD" -nsteps 2500000000 -cpi prod.cpt "$@"
