#!/bin/bash
#SBATCH -J swish2
#SBATCH -o swish2.log
#SBATCH -e swish2.err
#SBATCH -N 1
#SBATCH -p gpu
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:2
#SBATCH -w gpu16

mpirun -np 4  gmx_mpi mdrun -plumed ../plumed.dat -multidir rep0 rep1 rep2 rep3 -replex 5000 -hrex -dlb no -s prod.tpr -cpi prod.cpt -deffnm prod

