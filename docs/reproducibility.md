# Reproducibility guide

[Back to repository overview](../README.md)

This guide describes the files in this checkout and the preparation needed to reuse them. Scientific methods and interpretation are provided in the [paper and supplementary information](https://doi.org/10.1038/s41467-026-73863-x).

## File conventions

| File / directory | Purpose |
| --- | --- |
| `prod.tpr`, `topol.tpr` | Compiled GROMACS run inputs, including the topology and simulation parameters |
| `*.mdp` | Human-readable GROMACS simulation parameters, where supplied |
| `*.top`, `*.itp`, `*.ndx` | Topologies, included parameters/restraints, and atom-index groups |
| `npt.gro` | Coordinates supplied for simulation setup |
| `plumed.dat` | Collective-variable definitions, bias settings, and output instructions; some files are empty |
| `fit_tem.pdb` | Reference structure used by PLUMED alignment and funnel definitions |
| `*.pt` | Exported neural-network models; use the descriptor order specified in the matching PLUMED input |
| `states/` | Representative structures; the available files differ by setup |
| `REST3/setup/` | Preparation inputs and a short `scaled_8.sh` entry script |
| `run.sh`, `tpr.sh` | Local entry scripts that call the shared implementation in `scripts/` |
| `scripts/` | Shared replica launchers, input preparation, and REST3 topology scaling |

Model names distinguish autoencoder (`distance_AE.pt`), multitask (`multitask-*.pt`), and Deep-TICA (`deeptica-*.pt`) models. The suffixes `ddcv` and `hydracv` distinguish distance- and hydration-based models. A model's presence does not mean that it is active: inspect the uncommented `PYTORCH_MODEL` lines in the corresponding `plumed.dat`.

State filenames include `b`, `i`, and `u`, with numbered variants. Use the paper to interpret the states for each setup. In [tau5/FES/6](../tau5/FES/6/), `i2.pdb` and `u.pdb` are stored alongside the inputs, while the other state structures are in `states/`.

## Software environment

The reported stack is GROMACS 2022.6, PLUMED 2.9.0, and PyTorch 2.2.1. The repository does not record the mlcolvar version, compiler, MPI implementation, CUDA version, or full build configuration.

- Use an MPI-enabled GROMACS build with PLUMED integration and support for the `-hrex` option used by the replica-exchange scripts.
- For the FES inputs, verify support for `PYTORCH_MODEL`, `OPES_METAD_EXPLORE`, `FUNNEL`, and `FUNNEL_PS`, including the required LibTorch linkage. See the [PLUMED model-loading documentation](https://www.plumed.org/doc-v2.9/user-doc/html/_p_y_t_o_r_c_h__m_o_d_e_l.html) for build requirements.
- The shell scripts use Bash and standard Unix utilities. Slurm partition, node, GPU, and task settings must match the local cluster.
- Keep each model with its original descriptors, atom numbering, and reference structure. Models and PLUMED inputs are specific to their setup.

Record the local environment before reuse:

```bash
git rev-parse HEAD
gmx_mpi --version
plumed info --version
```

## Input availability

The following items are visible in the current checkout and should be resolved for the chosen workflow.

| Scope | Observation | Preparation needed |
| --- | --- | --- |
| c-Myc REST3 | `run.sh` refers to `plumed.dat`, which is absent. | Recover the original file or verify the intended PLUMED usage before launching. |
| Tau-5 REST3 and all SWISH setups | The supplied `plumed.dat` files contain no actions. REST3 autoencoder models are stored separately in `mlcv/`. | Confirm whether CV evaluation is intended during simulation or in later analysis. |
| Tau-5 SWISH `1`-`9` | Each `tpr.sh` refers to `<id>_benz.ndx`; these nine files are absent. The c-Myc index file is present. | Recover the matching index groups before regenerating Tau-5 SWISH TPRs. |
| Tau-5 FES `8` | An active `PYTORCH_MODEL` action references `multitask-ddcv.pt`, which is absent. | Recover the matching model before running this input. |
| Tau-5 FES `1`-`9` | Compiled TPRs are present, but the corresponding `prod.mdp` files are absent. | Recover the original parameter files for source-level regeneration. |
| FES topologies | The topologies include `./a99SBdisp.ff/...`, but no local force-field directory is present beside them. | When running `grompp`, make the bundled force field available at the expected path in the working copy. |
| REST3 source topologies | Both reference `posre.itp`, which is absent from `setup/`; c-Myc also lacks a local `a99SBdisp.ff/`. | Resolve the force-field path and any enabled restraint include before preprocessing these source topologies. |
| c-Myc REST3 preparation | `setup/process.py` expects an absent `process.top` and edits fixed line/column positions. A `processed.top` is supplied. | Establish the original preprocessing input and atom selections before rerunning this helper. |
| c-Myc FES `1` and Tau-5/K53 | OPES specifies `RESTART=YES` and reads `compressed.Kernels`, which is absent. | Obtain the matching bias state for a continuation, or configure a separate fresh run with restart disabled. |
| REST3 and most SWISH launchers | `run.sh` includes `-cpi prod.cpt`; no checkpoints are included. Tau-5 SWISH `3` and `4` omit this option. | A continuation requires matching checkpoints and outputs for every replica. Configure fresh runs separately. |

The compiled TPRs can be inspected without rebuilding their topology includes. They do not supply external PLUMED models, reference structures, or bias-restart files.

## Working example

The following Bash example copies Tau-5 FES setup `1` into an ignored working directory. Start from the repository root and use a new destination for each attempt.

```bash
mkdir -p work
cp -R tau5/FES/1 work/tau5-fes-1
cd work/tau5-fes-1
gmx_mpi dump -s prod.tpr > tpr-inspection.txt
```

Inspect the compiled settings and `plumed.dat`. This setup includes both models referenced by its PLUMED input and specifies `RESTART=NO`. With a compatible build, a zero-step initialization check is:

```bash
gmx_mpi mdrun -s prod.tpr -plumed plumed.dat -deffnm check -nsteps 0
```

This command can create output files. It checks initialization only; it does not establish stable dynamics or reproduce a free-energy result. The example has not been executed as part of this documentation update. Plan production length and resources from the original protocol and use a new working directory for production.

## Launch-script conventions

| Workflow | Launch directory | Script / inputs |
| --- | --- | --- |
| REST3 | `<target>/REST3/` | `bash run.sh` launches eight MPI ranks across `0`-`7`, reading `topol.tpr` in each replica. |
| SWISH | `<target>/swish/<id>/` | `bash tpr.sh` prepares inputs; `bash run.sh` launches four MPI ranks across `rep0`-`rep3`. The PLUMED path `../plumed.dat` is relative to the replica directories. |
| FES / K53 | The selected FES input directory | No launch script is supplied; `prod.tpr` and `plumed.dat` are the run inputs. |

The local entry scripts use paths relative to the launch directory, including when Slurm runs a temporary copy of `run.sh`. For Slurm, change into the directory listed above before using `sbatch run.sh`. Adapt the scheduler settings to the local cluster. Keep the repository layout, including `scripts/`, when copying a replica-exchange setup for use with these entry scripts.

The shared scripts also accept an explicit input directory. From the repository root, for example:

```bash
# Prepare the four c-Myc SWISH replicas, including its reference coordinates.
bash scripts/prepare_swish.sh c-myc/swish/1 1 -r npt.gro

# Launch Tau-5 SWISH setup 3 with its original fresh-run options.
bash scripts/run_replicas.sh swish tau5/swish/3
```

Use `--help` to inspect the shared interfaces without running simulations. Extra arguments are passed to `grompp` or `mdrun`. `GMX` and `MPIEXEC` can select alternative executable paths; supply one executable per variable, with extra GROMACS options as arguments. Shared scripts check required inputs before starting and stop on a failed command.

The local wrappers retain the original run differences: Tau-5 REST3 requests 2,500,000,000 steps, c-Myc REST3 requests 1,000,000,000 steps and verbose output, and only c-Myc SWISH preprocessing supplies `-r npt.gro`. Distinguish a fresh run from a continuation; GROMACS checkpoint state and PLUMED bias state must correspond to the same run when restarting.

With `-cpi`, GROMACS can start from the TPR when a checkpoint is absent; the flag alone does not guarantee continuation. See the [GROMACS 2022.6 mdrun documentation](https://manual.gromacs.org/2022.6/onlinehelp/gmx-mdrun.html) for checkpoint and `-nsteps` behavior.

For REST3 regeneration, run `bash scaled_8.sh` from `REST3/setup/` to generate replica topologies and TPRs from `processed.top`. Then run `bash mkdir.sh` from `REST3/` to copy the TPRs into replica directories. The shared implementation is in `scripts/prepare_rest3.sh` and `scripts/rest3/`; both targets use the same eight scaling pairs. Preparation retains `grompp -maxwarn 3` and overwrites outputs, so review preprocessing warnings in a working copy. Preserve the supplied originals for comparison.

## Script checks

Run the regression tests from the repository root with Python 3 and Bash:

```bash
python -m unittest discover -s tests -v
```

These tests use temporary inputs and simulated GROMACS/MPI commands to check launch arguments, replica preparation, and failure handling. They do not run MD or establish physical validity. On Windows, set `WORKFLOW_BASH` to the Git Bash executable if the default `bash` points to WSL.

## Reproducing published results

Full reproduction also requires trajectories, training data, analysis scripts, and run provenance beyond this checkout. The [data availability section](../README.md#data-availability) links the archives identified by the paper. Their contents must be checked for the specific analysis being reproduced.

For each new result, retain the input files, Git commit or archive version, build information, run command, random seeds, restart history, and any changes to parameters or model inputs. Follow the paper's analysis and convergence procedures when comparing free energies.
