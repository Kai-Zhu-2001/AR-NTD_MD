#!/bin/bash
now=$PWD
newdir=./
nsteps=2500000000 # 5us
#mpirun -np 8  gmx_mpi mdrun -plumed $now/plumed.dat -multidir 0 1 2 3 4 5 6 7 -replex 1000  -nsteps 100000 -hrex -dlb no -s topol.tpr -deffnm prod
mpirun -np 8  gmx_mpi mdrun -plumed $now/plumed.dat -multidir 0 1 2 3 4 5 6 7 -replex 1000  -nsteps $nsteps -hrex -dlb no -s topol.tpr -cpi prod.cpt -deffnm prod

