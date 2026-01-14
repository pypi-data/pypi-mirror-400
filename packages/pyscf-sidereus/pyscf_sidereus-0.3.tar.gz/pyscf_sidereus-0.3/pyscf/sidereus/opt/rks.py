from .rhf import OPT as rhf_OPT
from pyscf import dft, lib


class OPT(rhf_OPT):
    method = "dft"
    unrestricted = False


dft.rks.RKS.sOPT = dft.rks_symm.RKS.sOPT = lib.class_as_method(OPT)
try:
    from gpu4pyscf.dft import RKS
    RKS.sOPT = lib.class_as_method(OPT)
except ImportError:
    pass
