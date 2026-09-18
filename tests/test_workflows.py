"""Check workflow commands in temporary fixtures without running GROMACS.

Run with ``python -m unittest discover -s tests -v``. Set WORKFLOW_BASH
to the Bash executable when it is not available on PATH.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
BASH = os.environ.get("WORKFLOW_BASH") or shutil.which("bash")
SWISH_RUNS = [("tau5", str(i)) for i in range(1, 10)] + [("c-myc", "1")]
FAKE_TOOL = """#!/usr/bin/env bash
set -eu
printf '%s\\0' "${0##*/}" "$PWD" "$#" "$@" >> "$WORKFLOW_LOG"
for argument in "$@"; do
    if [[ -n ${FAKE_FAIL_OUTPUT:-} && $argument == "$FAKE_FAIL_OUTPUT" ]]; then
        exit 9
    fi
done
"""


@unittest.skipUnless(BASH, "Bash is required; set WORKFLOW_BASH to its executable")
class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="md workflows ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "fixture repo"
        shutil.copytree(REPOSITORY / "scripts", self.root / "scripts")
        self.log = self.root / "calls.bin"
        self.environment = os.environ.copy()
        binary_directory = self.root / "bin"
        for name in ("fake-mpirun", "fake-gmx"):
            executable = self.write(f"bin/{name}", FAKE_TOOL)
            executable.chmod(0o755)
        self.environment.update(
            PATH=str(binary_directory) + os.pathsep + self.environment.get("PATH", ""),
            MPIEXEC="fake-mpirun",
            GMX="fake-gmx",
            WORKFLOW_LOG=self.log.as_posix(),
        )
        self.environment.pop("FAKE_FAIL_OUTPUT", None)
        for system, setup_id in SWISH_RUNS:
            directory = f"{system}/swish/{setup_id}"
            for name in ("run.sh", "tpr.sh"):
                self.copy(f"{directory}/{name}")
            for name in ("plumed.dat", "prod.mdp", "npt.gro", f"{setup_id}_benz.ndx"):
                self.write(f"{directory}/{name}")
            for replica in range(4):
                self.write(f"{directory}/rep{replica}/prod.tpr")
                self.write(f"{directory}/rep{replica}/{setup_id}_swish{replica}.top")
        for system in ("tau5", "c-myc"):
            for name in ("run.sh", "mkdir.sh", "setup/scaled_8.sh"):
                self.copy(f"{system}/REST3/{name}")
            self.write(f"{system}/REST3/plumed.dat")
            for replica in range(8):
                self.write(f"{system}/REST3/{replica}/topol.tpr")

    def write(self, relative, content="fixture\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        return path

    def copy(self, relative):
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPOSITORY / relative, destination)

    def execute(self, relative, *arguments, cwd=None):
        self.log.unlink(missing_ok=True)
        script = self.root / relative
        return subprocess.run(
            [BASH, script.as_posix(), *arguments],
            cwd=cwd or script.parent,
            env=self.environment,
            capture_output=True,
            text=True,
            timeout=20,
        )

    def calls(self):
        if not self.log.exists():
            return []
        fields = self.log.read_bytes().decode("utf-8").split("\0")
        self.assertEqual(fields.pop(), "")
        calls = []
        while fields:
            tool, cwd, count = fields[:3]
            count = int(count)
            calls.append((tool, cwd, fields[3:3 + count]))
            del fields[:3 + count]
        return calls

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_swish_launches_preserve_replica_and_restart_options(self):
        for system, setup_id in SWISH_RUNS:
            with self.subTest(system=system, setup=setup_id):
                directory = f"{system}/swish/{setup_id}"
                self.assert_success(self.execute(f"{directory}/run.sh", "-ntomp", "8"))
                calls = self.calls()
                self.assertEqual(len(calls), 1)
                tool, cwd, arguments = calls[0]
                self.assertEqual(tool, "fake-mpirun")
                self.assertTrue(cwd.endswith("/fixture repo/" + directory), cwd)
                expected = [
                    "-np", "4", "fake-gmx", "mdrun", "-plumed", "../plumed.dat",
                    "-multidir", "rep0", "rep1", "rep2", "rep3", "-replex", "5000",
                    "-hrex", "-dlb", "no", "-s", "prod.tpr", "-deffnm", "prod",
                ]
                if system != "tau5" or setup_id not in ("3", "4"):
                    expected += ["-cpi", "prod.cpt"]
                self.assertEqual(arguments, expected + ["-ntomp", "8"])

    def test_swish_preparation_preserves_topology_and_restraint_options(self):
        for system, setup_id in SWISH_RUNS:
            with self.subTest(system=system, setup=setup_id):
                directory = f"{system}/swish/{setup_id}"
                self.assert_success(self.execute(f"{directory}/tpr.sh", "-maxwarn", "2"))
                calls = self.calls()
                self.assertEqual(len(calls), 4)
                for replica, (tool, cwd, arguments) in enumerate(calls):
                    self.assertEqual(tool, "fake-gmx")
                    self.assertTrue(cwd.endswith("/fixture repo/" + directory), cwd)
                    expected = [
                        "grompp", "-f", "prod.mdp", "-p",
                        f"rep{replica}/{setup_id}_swish{replica}.top", "-c", "npt.gro",
                        "-o", f"rep{replica}/prod.tpr", "-n", f"{setup_id}_benz.ndx",
                    ]
                    if system == "c-myc":
                        expected += ["-r", "npt.gro"]
                    self.assertEqual(arguments, expected + ["-maxwarn", "2"])

    def test_rest3_launches_preserve_duration_and_verbose_options(self):
        for system, steps in (("tau5", "2500000000"), ("c-myc", "1000000000")):
            with self.subTest(system=system):
                self.assert_success(self.execute(f"{system}/REST3/run.sh"))
                calls = self.calls()
                self.assertEqual(len(calls), 1)
                tool, cwd, arguments = calls[0]
                self.assertEqual(tool, "fake-mpirun")
                self.assertTrue(cwd.endswith(f"/fixture repo/{system}/REST3"), cwd)
                expected = [
                    "-np", "8", "fake-gmx", "mdrun", "-plumed", cwd + "/plumed.dat",
                    "-multidir", *map(str, range(8)), "-replex", "1000", "-hrex",
                    "-dlb", "no", "-s", "topol.tpr", "-deffnm", "prod", "-nsteps", steps,
                ]
                if system == "c-myc":
                    expected += ["-v"]
                self.assertEqual(arguments, expected + ["-cpi", "prod.cpt"])

    def test_spooled_wrapper_uses_submission_directory(self):
        submission = self.root / "tau5/swish/1"
        spool = Path(self.temporary.name) / "slurm spool"
        spool.mkdir()
        spooled_script = spool / "slurm_script"
        shutil.copy2(submission / "run.sh", spooled_script)
        self.assert_success(self.execute(spooled_script, cwd=submission))
        self.assertEqual(len(self.calls()), 1)
        self.assertTrue(self.calls()[0][1].endswith("/fixture repo/tau5/swish/1"))

    def test_missing_inputs_prevent_any_external_command(self):
        for script, missing in (
            ("tau5/swish/1/run.sh", "tau5/swish/1/rep3/prod.tpr"),
            ("tau5/swish/1/tpr.sh", "tau5/swish/1/rep3/1_swish3.top"),
            ("tau5/REST3/run.sh", "tau5/REST3/7/topol.tpr"),
            ("tau5/REST3/setup/scaled_8.sh", "tau5/REST3/setup/processed.top"),
        ):
            with self.subTest(script=script):
                (self.root / missing).unlink(missing_ok=True)
                result = self.execute(script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Missing", result.stderr)
                self.assertEqual(self.calls(), [])

    def test_failed_grompp_stops_remaining_replicas(self):
        self.environment["FAKE_FAIL_OUTPUT"] = "rep1/prod.tpr"
        result = self.execute("tau5/swish/1/tpr.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.calls()), 2)
        self.assertIn("rep1/prod.tpr", self.calls()[-1][2])

    def test_rest3_preparation_preserves_scales_and_grompp_options(self):
        # Numerical topology equivalence is checked separately from orchestration.
        self.write("scripts/rest3/gennewtop.sh", FAKE_TOOL)
        scales = (
            ("1.000", "1.000"), ("0.944", "1.000"),
            ("0.891", "1.003"), ("0.840", "1.010"),
            ("0.793", "1.020"), ("0.749", "1.027"),
            ("0.706", "1.035"), ("0.667", "1.045"),
        )
        for system in ("tau5", "c-myc"):
            with self.subTest(system=system):
                directory = f"{system}/REST3/setup"
                for name in ("processed.top", "rest.mdp", "npt.gro"):
                    self.write(f"{directory}/{name}")
                self.assert_success(self.execute(f"{directory}/scaled_8.sh"))
                calls = self.calls()
                self.assertEqual(len(calls), 16)
                for replica, (intra, km) in enumerate(scales):
                    tool, cwd, arguments = calls[replica]
                    self.assertEqual(tool, "gennewtop.sh")
                    self.assertTrue(cwd.endswith("/fixture repo/" + directory), cwd)
                    self.assertEqual(arguments, [intra, km, "processed.top", f"topol{replica}.top"])
                for replica, (tool, cwd, arguments) in enumerate(calls[8:]):
                    self.assertEqual(tool, "fake-gmx")
                    self.assertTrue(cwd.endswith("/fixture repo/" + directory), cwd)
                    self.assertEqual(arguments, [
                        "grompp", "-maxwarn", "3", "-o", f"topol{replica}.tpr",
                        "-f", "rest.mdp", "-p", f"topol{replica}.top",
                        "-c", "npt.gro", "-r", "npt.gro",
                    ])

    def test_failed_rest3_topology_generation_prevents_grompp(self):
        self.write("scripts/rest3/gennewtop.sh", FAKE_TOOL)
        for name in ("processed.top", "rest.mdp", "npt.gro"):
            self.write(f"tau5/REST3/setup/{name}")
        self.environment["FAKE_FAIL_OUTPUT"] = "topol1.top"
        result = self.execute("tau5/REST3/setup/scaled_8.sh")
        self.assertNotEqual(result.returncode, 0)
        calls = self.calls()
        self.assertEqual([call[0] for call in calls], ["gennewtop.sh", "gennewtop.sh"])
        self.assertEqual(calls[-1][2][-1], "topol1.top")

    def test_rest3_distribution_checks_all_inputs_before_copying(self):
        for system in ("tau5", "c-myc"):
            with self.subTest(system=system):
                for replica in range(8):
                    self.write(f"{system}/REST3/setup/topol{replica}.tpr", f"replica {replica}\n")
                (self.root / f"{system}/REST3/setup/topol7.tpr").unlink()
                result = self.execute(f"{system}/REST3/mkdir.sh")
                self.assertNotEqual(result.returncode, 0)
                for replica in range(8):
                    self.assertEqual((self.root / f"{system}/REST3/{replica}/topol.tpr").read_text(), "fixture\n")
                self.write(f"{system}/REST3/setup/topol7.tpr", "replica 7\n")
                self.assert_success(self.execute(f"{system}/REST3/mkdir.sh"))
                for replica in range(8):
                    self.assertEqual((self.root / f"{system}/REST3/{replica}/topol.tpr").read_text(), f"replica {replica}\n")
                self.assertEqual(self.calls(), [])


if __name__ == "__main__":
    unittest.main()
