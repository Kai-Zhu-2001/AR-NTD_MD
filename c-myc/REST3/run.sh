#!/usr/bin/env bash
#SBATCH -J rest3
#SBATCH -o rest3.log
#SBATCH -e rest3.err
#SBATCH -N 1
#SBATCH -p gpu
#SBATCH --gres=gpu:4
#SBATCH --ntasks=8

# Submit or run from this simulation directory.
exec bash ../../scripts/run_replicas.sh rest3 "$PWD" -nsteps 1000000000 -v -cpi prod.cpt "$@"
