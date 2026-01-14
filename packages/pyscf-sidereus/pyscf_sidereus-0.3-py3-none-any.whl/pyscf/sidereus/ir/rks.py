# Copyright 2014-2022 The PySCF Developers, 2025-2026 Sidereus-AI ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");


from .rhf import Infrared
from pyscf import hessian, dft, lib


class Infrared(Infrared):
    hess_cls = hessian.rks.Hessian


dft.rks.RKS.sIR = dft.rks_symm.RKS.sIR = lib.class_as_method(Infrared)
try:
    from gpu4pyscf.dft import RKS
    RKS.sIR = lib.class_as_method(Infrared)
except ImportError:
    pass
