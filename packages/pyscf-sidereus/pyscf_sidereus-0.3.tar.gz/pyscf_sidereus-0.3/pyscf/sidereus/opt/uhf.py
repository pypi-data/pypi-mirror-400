from .rhf import OPT as rhf_OPT
from pyscf import scf, lib


class OPT(rhf_OPT):
    method = "scf"
    unrestricted = True


scf.uhf.UHF.sOPT = lib.class_as_method(OPT)
try:
    from gpu4pyscf.scf import UHF
    UHF.sOPT = lib.class_as_method(OPT)
except ImportError:
    pass
