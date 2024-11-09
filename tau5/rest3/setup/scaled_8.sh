    bash gennewtop.sh 1.000 1.000 processed.top topol0.top
    bash gennewtop.sh 0.944 1.000 processed.top topol1.top
    bash gennewtop.sh 0.891 1.003 processed.top topol2.top
    bash gennewtop.sh 0.840 1.010 processed.top topol3.top
    bash gennewtop.sh 0.793 1.020 processed.top topol4.top
    bash gennewtop.sh 0.749 1.027 processed.top topol5.top
    bash gennewtop.sh 0.706 1.035 processed.top topol6.top
    bash gennewtop.sh 0.667 1.045 processed.top topol7.top
    gmx_mpi grompp -maxwarn 3 -o topol0.tpr -f rest.mdp -p topol0.top -c npt.gro -r npt.gro
    gmx_mpi grompp -maxwarn 3 -o topol1.tpr -f rest.mdp -p topol1.top -c npt.gro -r npt.gro
    gmx_mpi grompp -maxwarn 3 -o topol2.tpr -f rest.mdp -p topol2.top -c npt.gro -r npt.gro
    gmx_mpi grompp -maxwarn 3 -o topol3.tpr -f rest.mdp -p topol3.top -c npt.gro -r npt.gro
    gmx_mpi grompp -maxwarn 3 -o topol4.tpr -f rest.mdp -p topol4.top -c npt.gro -r npt.gro
    gmx_mpi grompp -maxwarn 3 -o topol5.tpr -f rest.mdp -p topol5.top -c npt.gro -r npt.gro
    gmx_mpi grompp -maxwarn 3 -o topol6.tpr -f rest.mdp -p topol6.top -c npt.gro -r npt.gro
    gmx_mpi grompp -maxwarn 3 -o topol7.tpr -f rest.mdp -p topol7.top -c npt.gro -r npt.gro