#### Supporting data for the paper:
## "Targeting the intrinsically disordered AR-NTD through a machine learn-ing-based enhanced sampling workflow"

![Workflow Overview](workflow.jpg)

The training of the models was based on the [mlcolvar library](https://github.com/luigibonati/mlcolvar).

The REST3 tutorial is available here: https://github.com/mdlab-um/REST3_tutorial.

The SWISH tutorial is available here: https://github.com/Gervasiolab/Gervasio-Protein-Dynamics/tree/master/swish_bootcamp.

All molecular dynamics simulations were conducted using [GROMACS 2022.6](https://github.com/gromacs/gromacs), integrated with the [PLUMED 2.9.0](https://github.com/plumed/plumed2) plugin and the [PyTorch 2.2.1](https://github.com/pytorch/pytorch) library.

### Repo structure
The contents of the repository are organized as follows:

#### tau5/REST3 : files for REST3 simulations of tau5
  - **0-7**: input files for REST simulations
  - **setup**: script for scaling the top Hamiltonian
  -  **mlcv**: frozen torchscript models for AE CV

#### tau5/swish : files for SWISH simulations of tau5
  - **1-9**: input files for SWISH simulations

#### tau5/FES : files for Binding FES simulations of tau5
  - **1-9**: input files for Binding FES simulations
  - **1-9/states** Structural files of the free-energy minima conformations

#### tau5/a99SBdisp.ff : files for the force field of intrinsically disordered proteins of tau5

#### c-myc/REST3 : files for REST3 simulations of c-myc

#### tau5/swish : files for SWISH simulations of c-myc

#### tau5/FES : files for Binding FES simulations of c-myc
