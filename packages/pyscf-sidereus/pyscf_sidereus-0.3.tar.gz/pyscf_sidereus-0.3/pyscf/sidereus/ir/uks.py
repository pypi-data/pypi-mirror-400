# Copyright 2014-2022 The PySCF Developers, 2025-2026 Sidereus-AI ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");


from .uhf import Infrared
from pyscf import hessian, dft, lib


class Infrared(Infrared):
    hess_cls = hessian.uks.Hessian

dft.uks.UKS.sIR = dft.uks_symm.UKS.sIR = lib.class_as_method(Infrared)
