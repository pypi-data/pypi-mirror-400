from .rhf import OPT as rhf_OPT
from pyscf import dft, lib


class OPT(rhf_OPT):
    method = "dft"
    unrestricted = True


dft.uks.UKS.sOPT = dft.uks_symm.UKS.sOPT = lib.class_as_method(OPT)
try:
    from gpu4pyscf.dft import UKS
    UKS.sOPT = lib.class_as_method(OPT)
except ImportError:
    pass
