#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: bash scripts/run_replicas.sh {rest3|swish} RUN_DIRECTORY [mdrun options...]"
}

if [[ ${1:-} == --help ]]; then
    usage
    exit 0
fi
if (( $# < 2 )); then
    usage >&2
    exit 2
fi

method=$1
run_directory=$2
shift 2

case "$method" in
    rest3)
        replicas=(0 1 2 3 4 5 6 7)
        exchange_interval=1000
        tpr=topol.tpr
        ;;
    swish)
        replicas=(rep0 rep1 rep2 rep3)
        exchange_interval=5000
        tpr=prod.tpr
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac

cd -- "$run_directory"
inputs=(plumed.dat)
for replica in "${replicas[@]}"; do
    inputs+=("$replica/$tpr")
done
for input in "${inputs[@]}"; do
    if [[ ! -f $input ]]; then
        echo "Missing input: $PWD/$input" >&2
        exit 1
    fi
done

# GROMACS enters each replica directory before loading the PLUMED input.
plumed_input=../plumed.dat
if [[ $method == rest3 ]]; then
    plumed_input=$PWD/plumed.dat
fi

exec "${MPIEXEC:-mpirun}" -np "${#replicas[@]}" "${GMX:-gmx_mpi}" mdrun \
    -plumed "$plumed_input" -multidir "${replicas[@]}" \
    -replex "$exchange_interval" -hrex -dlb no -s "$tpr" -deffnm prod "$@"
