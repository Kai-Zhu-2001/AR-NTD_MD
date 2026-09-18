#!/usr/bin/env bash
#SBATCH -J swish8
#SBATCH -o swish8.log
#SBATCH -e swish8.err
#SBATCH -N 1
#SBATCH -p gpu
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:2
#SBATCH -w gpu16

# Submit or run from this simulation directory.
exec bash ../../../scripts/run_replicas.sh swish "$PWD" -cpi prod.cpt "$@"

