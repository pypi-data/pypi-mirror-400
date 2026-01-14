import subprocess
import tempfile
import sys
import yaml
from copy import deepcopy
from pathlib import Path
import numpy as np
from pyscf import lib, scf
import h5py

optimization_data = {
    "geom": {
        "type": "redund",
        "fn": None,
        "coord_kwargs": {},
    },
    "calc": {
        "type": "pyscf",
    },
}

growing_string_data = {
    "precontr": {},
    "cos": {
        "type": "gs",
    },
    "opt": {
        "type": "string",
        "stop_in_when_full": -1,
    },
    "calc": {
        "type": "pyscf",
    },
    "tsopt": {
        "type": "rsprfo",
    },
    "geom": {
        "type": "dlc",
        "fn": [None, None],
    },
}


class OPT(lib.StreamObject):
    method = "scf"
    unrestricted = False
    threshold_map = {
        "loose": "gau_loose",
        "tight": "gau_tight",
        "verytight": "gau_vtight",
    }

    def __init__(self, mf, ts=False, product_xyzs=None, threshold=None, max_cycles=None,
                 verbose=None, constraints=None, reaction_modes=None):
        self.mf = mf
        self.ts = ts
        self.product_xyzs = product_xyzs
        if threshold and threshold.lower() not in ("loose", "tight", "verytight", None):
            raise ValueError(f"Threshold should be one of \
loose, tight, verytight, None, but got {threshold}")
        self.threshold = threshold
        if constraints is not None:
            if not isinstance(constraints, list):
                raise TypeError("constraints should be a list of lists")
        self.constraints = constraints
        if reaction_modes is not None:
            if not isinstance(reaction_modes, list):
                raise TypeError(
                    "reaction_modes should be a list of primitive coordinate lists")
        self.reaction_modes = reaction_modes
        self.max_cycles = max_cycles
        self.verbose = verbose
        if self.verbose is None:
            self.verbose = mf.verbose

    def _gen_geom_block(self, optimization_data, mol):
        data = deepcopy(optimization_data)
        data["geom"]["fn"] = mol.tostring(format="xyz")
        if self.constraints is not None:
            data["geom"]["coord_kwargs"]["constrain_prims"] = self.constraints
        return data

    def _gen_ts_search_block(self, growing_string_data, mol):
        data = deepcopy(growing_string_data)
        data["geom"]["fn"] = [mol.tostring(format="xyz"), self.product_xyzs]
        return data

    def _gen_calc_block(self, data, mol):
        data["calc"]["method"] = self.method
        data["calc"]["unrestricted"] = self.unrestricted
        data["calc"]["basis"] = mol.basis
        data["calc"]["charge"] = mol.charge
        data["calc"]["mult"] = mol.spin + 1
        data["calc"]["pal"] = lib.num_threads()
        if getattr(self.mf, "xc", None):
            data["calc"]["xc"] = self.mf.xc
        if self.mf.__module__.startswith("gpu4pyscf"):
            data["calc"]["use_gpu"] = True
        if getattr(self.mf, "auxbasis", None):
            data["calc"]["auxbasis"] = self.mf.auxbasis

    def _gen_opt_block(self):
        opt_block = {"thresh": self.threshold_map.get(self.threshold, "gau")}
        if self.max_cycles is not None:
            opt_block["max_cycles"] = self.max_cycles
        if self.reaction_modes is not None:
            if not self.ts:
                raise KeyError(
                    "reaction_modes can only be used with TS optimization")
            opt_block["rx_modes"] = self.reaction_modes
        return opt_block

    def _run_yaml(self, data, logger, output_process):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            with open(tmpdir / "run.yaml", "w") as f:
                yaml.dump(data, f)
            process = subprocess.Popen(
                ["pysis", "run.yaml"],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in process.stdout:
                line = line.strip()
                if line and self.verbose >= lib.logger.NOTE:
                    logger.note("%s", line)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise RuntimeError(f"Optimization failed")
            output_process(tmpdir)

    def _opt_output_process(self, tmpdir):
        if self.ts:
            outname = "ts_opt.xyz"
        else:
            outname = "final_geometry.xyz"
        with open(tmpdir / outname, "r") as f:
            data = np.array([line.strip().split()[1:]
                            for line in f.readlines()[2:]], dtype=float)
        self.mf.mol.set_geom_(data)

    def kernel(self):
        if self.ts and self.product_xyzs:
            return self.ts_search()
        return self.optimize()

    def optimize(self):
        mol = self.mf.mol
        logger = lib.logger.new_logger(mol, self.verbose)
        # GEOM block
        data = self._gen_geom_block(optimization_data, mol)
        # CALC block
        self._gen_calc_block(data, mol)
        # OPT and TSOPT block
        opt_block = self._gen_opt_block()
        if not self.ts:
            data["opt"] = {"type": "rfo", **opt_block}
        else:
            data["tsopt"] = {"type": "rsprfo", **opt_block}

        self._run_yaml(data, logger, self._opt_output_process)

        return mol

    def ts_search(self):
        mol = self.mf.mol
        logger = lib.logger.new_logger(mol, self.verbose)
        data = self._gen_ts_search_block(growing_string_data, mol)
        self._gen_calc_block(data, mol)
        self._run_yaml(data, logger, self._opt_output_process)
        return mol

    def _irc_output_process(self, tmpdir):
        self.irc_results = {"first": None, "last": None}
        with open(tmpdir / "finished_first.xyz", "r") as f:
            self.irc_results["first"] = f.read()
        with open(tmpdir / "finished_last.xyz", "r") as f:
            self.irc_results["last"] = f.read()
        with h5py.File(tmpdir / "finished_irc_data.h5", "r") as f:
            self.irc_results["energies"] = f["energies"][:]
            self.irc_results["coordinates"] = f["coords"][:]

    def irc(self):
        mol = self.mf.mol
        logger = lib.logger.new_logger(mol, self.verbose)
        # GEOM block
        data = self._gen_geom_block(optimization_data, mol)
        # CALC block
        self._gen_calc_block(data, mol)
        # IRC block
        data["irc"] = {"type": "eulerpc"}
        self._run_yaml(data, logger, self._irc_output_process)
        return self.irc_results


scf.hf.RHF.sOPT = lib.class_as_method(OPT)
try:
    from gpu4pyscf.scf import RHF
    RHF.sOPT = lib.class_as_method(OPT)
except ImportError:
    pass
