#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: bash scripts/prepare_swish.sh SETUP_DIRECTORY SETUP_ID [grompp options...]"
}

if [[ ${1:-} == --help ]]; then
    usage
    exit 0
fi
if (( $# < 2 )); then
    usage >&2
    exit 2
fi

cd -- "$1"
setup_id=$2
shift 2
if [[ ! $setup_id =~ ^[0-9]+$ ]]; then
    echo "SETUP_ID must be a numeric setup identifier." >&2
    exit 2
fi

inputs=(prod.mdp npt.gro "${setup_id}_benz.ndx")
for replica in 0 1 2 3; do
    inputs+=("rep${replica}/${setup_id}_swish${replica}.top")
done
for input in "${inputs[@]}"; do
    if [[ ! -f $input ]]; then
        echo "Missing input: $PWD/$input" >&2
        exit 1
    fi
done

for replica in 0 1 2 3; do
    "${GMX:-gmx_mpi}" grompp -f prod.mdp \
        -p "rep${replica}/${setup_id}_swish${replica}.top" \
        -c npt.gro -o "rep${replica}/prod.tpr" -n "${setup_id}_benz.ndx" "$@"
done
