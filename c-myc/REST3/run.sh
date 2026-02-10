#!/bin/bash
#SBATCH -J rest3
#SBATCH -o rest3.log
#SBATCH -e rest3.err
#SBATCH -N 1
#SBATCH -p gpu
#SBATCH --gres=gpu:4
##SBATCH --cpus-per-task=8
#SBATCH --ntasks=8
##SBATCH -w gpu01

#!/bin/bash
now=$PWD
newdir=./
nsteps=1000000000 # 5us
#mpirun -np 8  gmx_mpi mdrun -v -plumed $now/plumed.dat -multidir 0 1 2 3 4 5 6 7 -replex 1000  -nsteps $nsteps -hrex -dlb no -s topol.tpr -deffnm prod
mpirun -np 8  gmx_mpi mdrun -v -plumed $now/plumed.dat -multidir 0 1 2 3 4 5 6 7 -replex 1000  -nsteps $nsteps -hrex -dlb no -s topol.tpr -cpi prod.cpt -deffnm prod

