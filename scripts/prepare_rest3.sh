#!/bin/bash
set -euo pipefail

if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    printf 'Usage: bash scripts/prepare_rest3.sh SETUP_DIRECTORY\n'
    exit 0
fi
if [[ $# -ne 1 ]]; then
    printf 'Usage: bash scripts/prepare_rest3.sh SETUP_DIRECTORY\n' >&2
    exit 2
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd -- "$1"
for input in processed.top rest.mdp npt.gro; do
    if [[ ! -f "$input" ]]; then
        printf 'Missing REST3 input: %s/%s\n' "$PWD" "$input" >&2
        exit 1
    fi
done

gmx=${GMX:-gmx_mpi}
if ! command -v "$gmx" >/dev/null 2>&1; then
    printf 'GROMACS executable not found: %s\n' "$gmx" >&2
    exit 1
fi

scale_intra=(1.000 0.944 0.891 0.840 0.793 0.749 0.706 0.667)
scale_km=(1.000 1.000 1.003 1.010 1.020 1.027 1.035 1.045)

for replica in {0..7}; do
    bash "$script_dir/rest3/gennewtop.sh" "${scale_intra[$replica]}" \
        "${scale_km[$replica]}" processed.top "topol${replica}.top"
done

for replica in {0..7}; do
    "$gmx" grompp -maxwarn 3 -o "topol${replica}.tpr" -f rest.mdp \
        -p "topol${replica}.top" -c npt.gro -r npt.gro
done
