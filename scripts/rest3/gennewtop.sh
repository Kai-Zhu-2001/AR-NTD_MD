#!/bin/bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
    printf 'Usage: bash gennewtop.sh SCALE_INTRA SCALE_KM INPUT OUTPUT\n' >&2
    exit 2
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

scale_intra="$1" # \lambda^pp
scale_km="$2"    # \kappa_m
input="$3"       # processed topology file e.g., p53.top
output="$4"      # generated new topology

scale_inter=$(printf '%s %s\n' "$scale_intra" "$scale_km" | awk '{print $2*sqrt($1)}')
echo 'scale_km = ' "$scale_km"
echo 'scale_intra = ' "$scale_intra"
echo 'scale_inter = ' "$scale_inter"

scaled_topology="topol-$scale_intra-$scale_inter.top"
bash "$script_dir/partial_tempering.sh" "$scale_intra" "$scale_inter" < "$input" > "$scaled_topology"

line1=$(grep -n 'nonbond_params' "$scaled_topology" | cut -d":" -f 1 | awk 'NR==1{print}')
line2=$(grep -n 'nonbond_params' "$scaled_topology" | cut -d":" -f 1 | awk 'NR==2{print}')
if [[ -z "$line1" || -z "$line2" ]]; then
    printf 'Expected two nonbond_params sections in %s\n' "$scaled_topology" >&2
    exit 1
fi
line1a=$((line1 + 1))
line1a2=$((line1 + 2))
line2b=$((line2 - 1))
sed -n "${line1a}h;${line1a2},${line2b}H;\$G;1,${line1}p;${line2},\$p" "$scaled_topology" > test.top
mv test.top "$output"
echo "done"
echo ""
