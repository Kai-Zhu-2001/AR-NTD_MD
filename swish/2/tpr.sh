#/bin/bash
for i in $(seq 0 3); do
        gmx_mpi grompp -f prod.mdp -p rep$i/2_swish$i.top -c npt.gro -o rep$i/prod.tpr -n 2_benz.ndx 
done

