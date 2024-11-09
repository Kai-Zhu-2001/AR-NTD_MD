#/bin/bash
for i in $(seq 0 3); do
        gmx_mpi grompp -f prod.mdp -p rep$i/7_swish$i.top -c npt.gro -o rep$i/prod.tpr -n 7_benz.ndx 
done

