# AR-NTD_MD

Molecular dynamics inputs, trained collective-variable models, and representative structures for the Tau-5 region of the androgen receptor N-terminal domain (AR-NTD) and c-Myc.

**Associated publication:** Zhu, K., Wang, H., Zhang, J. et al. *Targeting the intrinsically disordered AR-NTD through a machine learning-based enhanced sampling workflow.* **Nature Communications 17**, 7206 (2026). [Read the paper](https://doi.org/10.1038/s41467-026-73863-x).

[Repository contents](#repository-contents) | [Reproducibility guide](docs/reproducibility.md) | [Data availability](#data-availability) | [Citation](#citation)

## Workflow

REST3 conformational sampling and autoencoder analysis identify representative states. SWISH explores potential binding pockets, followed by ligand-binding simulations with learned collective variables and free-energy analysis.

REST3 is replica exchange with solute tempering; SWISH is Sampling Water Interfaces through Scaled Hamiltonians. CV denotes a collective variable, and FES denotes a free-energy surface.

![Overview of the enhanced-sampling and machine-learning workflow](workflow.jpg)

## Repository contents

| Stage / resource | Tau-5 | c-Myc | Contents |
| --- | --- | --- | --- |
| REST3 | [tau5/REST3](tau5/REST3/) | [c-myc/REST3](c-myc/REST3/) | Eight replicas (`0`-`7`), preparation scripts, autoencoder models, and representative states |
| SWISH | [tau5/swish](tau5/swish/) | [c-myc/swish](c-myc/swish/) | Tau-5 setups `1`-`9`; c-Myc setup `1`; four replicas (`rep0`-`rep3`) per setup |
| Binding free energy | [tau5/FES](tau5/FES/) | [c-myc/FES](c-myc/FES/) | Tau-5 setups `1`-`9`; c-Myc setup `1`; PLUMED inputs, trained models, and state structures |
| K53 binding | [tau5/FES_k53](tau5/FES_k53/) | -- | Tau-5/K53 simulation inputs and hydration-based model |
| Force field | [tau5/a99SBdisp.ff](tau5/a99SBdisp.ff/) | -- | Bundled a99SB-disp protein and water parameters |

**Numbering:** `REST3/0`-`7` are replica indices. Numbers under `swish/` and `FES/` identify separate setups; SWISH replicas are the nested `rep0`-`rep3` directories. Representative structures are in `REST3/states/` and each `FES/<id>/states/`, with two additional structures directly in `tau5/FES/6/`.

## Code organization

```text
scripts/
  run_replicas.sh       # Shared REST3 and SWISH launcher
  prepare_swish.sh      # Prepare four SWISH replica inputs
  prepare_rest3.sh      # Prepare eight REST3 replica inputs
  rest3/               # Shared Hamiltonian-scaling implementation
tau5/                  # Tau-5 inputs, models, structures, and entry scripts
c-myc/                 # c-Myc inputs, models, structures, and entry scripts
docs/                  # Reproducibility details
tests/                 # Script regression tests using simulated commands
```

Simulation directories keep short `run.sh`, `tpr.sh`, and `scaled_8.sh` entry scripts. These specify local settings and call the shared implementation in `scripts/`. Run an entry script from its own directory; see the [launch conventions](docs/reproducibility.md#launch-script-conventions).

## Getting started

1. Choose a target and simulation stage from the table above.
2. Read the [reproducibility guide](docs/reproducibility.md) for file conventions, input gaps, and an initialization example.
3. Run simulations in a separate working copy with a compatible GROMACS/PLUMED installation.

The reported software versions are:

| Software | Version | Role |
| --- | --- | --- |
| GROMACS | 2022.6 | Molecular dynamics and replica exchange |
| PLUMED | 2.9.0 | Collective variables and enhanced sampling |
| PyTorch | 2.2.1 | Neural-network models |
| mlcolvar | Not recorded in this repository | Collective-variable training and analysis |

The scripts target a Linux/HPC environment with MPI; some include site-specific Slurm settings. Build requirements and restart conditions are described in the guide.

## Data availability

This checkout contains simulation inputs, exported models, and selected structures. Production trajectories, checkpoints, training datasets, and end-to-end training/analysis scripts are not included here.

The paper's [data and code availability statements](https://www.nature.com/articles/s41467-026-73863-x#data-availability) identify two archives:

| Archive | DOI |
| --- | --- |
| Study data and analysis materials | [10.5281/zenodo.19599898](https://doi.org/10.5281/zenodo.19599898) |
| Archived GitHub repository | [10.5281/zenodo.19613110](https://doi.org/10.5281/zenodo.19613110) |

For reproducible reuse, record the Git commit or archived version used, together with software/build versions and any local input changes.

## Citation

Please cite the associated publication above when using these materials. Machine-readable bibliographic metadata is provided in [CITATION.cff](CITATION.cff). Cite the relevant archived version when referring to a specific dataset or repository snapshot.

## Related resources

- [mlcolvar](https://github.com/luigibonati/mlcolvar): collective-variable training library.
- [REST3 tutorial](https://github.com/mdlab-um/REST3_tutorial): Hamiltonian scaling and replica-exchange setup.
- [SWISH tutorial](https://github.com/Gervasiolab/Gervasio-Protein-Dynamics/tree/master/swish_bootcamp): SWISH preparation and simulation examples.

## License

The repository includes an [MIT license](LICENSE). Retain attribution and notices supplied with third-party materials, including the [a99SB-disp force-field citation](tau5/a99SBdisp.ff/forcefield.doc).
