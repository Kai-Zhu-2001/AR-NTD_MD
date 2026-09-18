#!/bin/bash
set -euo pipefail

# Run from this REST3 directory.
for replica in {0..7}; do
    if [[ ! -f "setup/topol${replica}.tpr" ]]; then
        printf 'Missing REST3 input: setup/topol%s.tpr\n' "$replica" >&2
        exit 1
    fi
done

for replica in {0..7}; do
    mkdir -p "$replica"
    cp "setup/topol${replica}.tpr" "$replica/topol.tpr"
done
