# Copyright 2014-2022 The PySCF Developers, 2025-2026 Sidereus-AI ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");


from pyscf import scf
import numpy
from pyscf import lib
from pyscf.lib import logger
from pyscf.scf import ucphf
from pyscf.scf import _response_functions
from . import rhf as rhf_nmr


def dia(nmrobj, shielding_nuc=None, dm0=None):
    if dm0 is None:
        dm0 = nmrobj._scf.make_rdm1()
    if not (isinstance(dm0, numpy.ndarray) and dm0.ndim == 2):
        dm0 = dm0[0] + dm0[1]
    return rhf_nmr.dia(nmrobj, shielding_nuc, dm0)


def para(nmrobj, mo10=None, mo_coeff=None, mo_occ=None,
         shielding_nuc=None):
    if mo_coeff is None:
        mo_coeff = nmrobj._scf.mo_coeff
    if mo_occ is None:
        mo_occ = nmrobj._scf.mo_occ
    if shielding_nuc is None:
        shielding_nuc = nmrobj.shielding_nuc

    mol = nmrobj.mol
    para_vir = numpy.empty((len(shielding_nuc), 3, 3))
    para_occ = numpy.empty((len(shielding_nuc), 3, 3))
    occidxa = mo_occ[0] > 0
    occidxb = mo_occ[1] > 0
    viridxa = mo_occ[0] == 0
    viridxb = mo_occ[1] == 0
    orboa = mo_coeff[0][:, occidxa]
    orbob = mo_coeff[1][:, occidxb]
    orbva = mo_coeff[0][:, viridxa]
    orbvb = mo_coeff[1][:, viridxb]
    nao = mo_coeff[0].shape[0]
    # Vectorized version: extract occupied and virtual parts and perform matrix multiplication in batch
    mo10a_occ = mo10[0][:, occidxa, :]  # shape: (3, nocc_alpha, nocc_alpha)
    mo10b_occ = mo10[1][:, occidxb, :]  # shape: (3, nocc_beta, nocc_beta)
    mo10a_vir = mo10[0][:, viridxa, :]  # shape: (3, nvir_alpha, nocc_alpha)
    mo10b_vir = mo10[1][:, viridxb, :]  # shape: (3, nvir_beta, nocc_beta)

    # Compute contributions from alpha and beta electrons
    dm10_oo_alpha = orboa @ mo10a_occ @ orboa.conj().T  # shape: (3, nao, nao)
    dm10_oo_beta = orbob @ mo10b_occ @ orbob.conj().T   # shape: (3, nao, nao)
    dm10_vo_alpha = orbva @ mo10a_vir @ orboa.conj().T  # shape: (3, nao, nao)
    dm10_vo_beta = orbvb @ mo10b_vir @ orbob.conj().T   # shape: (3, nao, nao)

    # Combine contributions from both spin channels
    dm10_oo = dm10_oo_alpha + dm10_oo_beta
    dm10_vo = dm10_vo_alpha + dm10_vo_beta
    for n, atm_id in enumerate(shielding_nuc):
        mol.set_rinv_origin(mol.atom_coord(atm_id))
        h01 = mol.intor_asymmetric('int1e_prinvxp', 3)
        para_occ[n] = numpy.einsum('xji,yij->xy', dm10_oo, h01) * 2
        para_vir[n] = numpy.einsum('xji,yij->xy', dm10_vo, h01) * 2
    msc_para = para_occ + para_vir
    return msc_para, para_vir, para_occ


def make_h10(mol, dm0, verbose=logger.WARN):
    log = logger.new_logger(mol, verbose=verbose)
    # A10_i dot p + p dot A10_i consistents with <p^2 g>
    # A10_j dot p + p dot A10_j consistents with <g p^2>
    # A10_j dot p + p dot A10_j => i/2 (rjxp - pxrj) = irjxp
    log.debug('First-order GIAO Fock matrix')
    h1 = -.5 * mol.intor('int1e_giao_irjxp', 3) + make_h10giao(mol, dm0)
    return h1


def make_h10giao(mol, dm0):
    vj, vk = rhf_nmr.get_jk(mol, dm0)
    h1 = vj[0] + vj[1] - vk
    h1 -= mol.intor_asymmetric('int1e_ignuc', 3)
    if mol.has_ecp():
        h1 -= mol.intor_asymmetric('ECPscalar_ignuc', 3)
    h1 -= mol.intor('int1e_igkin', 3)
    return h1


def get_fock(nmrobj, dm0=None):
    r'''First order partial derivatives of Fock matrix wrt external magnetic
    field.  \frac{\partial F}{\partial B}
    '''
    if dm0 is None:
        dm0 = nmrobj._scf.make_rdm1()

    log = logger.Logger(nmrobj.stdout, nmrobj.verbose)
    h1 = make_h10(nmrobj.mol, dm0, log)
    if nmrobj.chkfile:
        lib.chkfile.dump(nmrobj.chkfile, 'nmr/h1', h1)
    return h1




def solve_mo1(nmrobj, mo_energy=None, mo_coeff=None, mo_occ=None,
              h1=None, s1=None):
    '''Solve the first order equation'''
    cput1 = (logger.process_clock(), logger.perf_counter())
    log = logger.Logger(nmrobj.stdout, nmrobj.verbose)
    if mo_energy is None:
        mo_energy = nmrobj._scf.mo_energy
    if mo_coeff is None:
        mo_coeff = nmrobj._scf.mo_coeff
    if mo_occ is None:
        mo_occ = nmrobj._scf.mo_occ

    mol = nmrobj.mol
    orboa = mo_coeff[0][:, mo_occ[0] > 0]
    orbob = mo_coeff[1][:, mo_occ[1] > 0]
    if h1 is None:
        dm0 = nmrobj._scf.make_rdm1(mo_coeff, mo_occ)
        h1 = nmrobj.get_fock(dm0)
        h1 = (lib.einsum('xpq,pi,qj->xij', h1[0], mo_coeff[0].conj(), orboa),
              lib.einsum('xpq,pi,qj->xij', h1[1], mo_coeff[1].conj(), orbob))
        cput1 = log.timer('first order Fock matrix', *cput1)
    if s1 is None:
        s1 = nmrobj.get_ovlp(mol)
        s1 = (lib.einsum('xpq,pi,qj->xij', s1, mo_coeff[0].conj(), orboa),
              lib.einsum('xpq,pi,qj->xij', s1, mo_coeff[1].conj(), orbob))

    # Always use CPHF
    vind = gen_vind(nmrobj._scf, mo_coeff, mo_occ)
    mo10, mo_e10 = ucphf.solve(vind, mo_energy, mo_occ, h1, s1,
                               nmrobj.max_cycle_cphf, nmrobj.conv_tol,
                               verbose=log)

    logger.timer(nmrobj, 'solving mo1 eqn', *cput1)
    return mo10, mo_e10


def gen_vind(mf, mo_coeff, mo_occ):
    '''Induced potential'''
    vresp = mf.gen_response(hermi=2)
    occidxa = mo_occ[0] > 0
    occidxb = mo_occ[1] > 0
    orboa = mo_coeff[0][:, occidxa]
    orbob = mo_coeff[1][:, occidxb]
    nocca = orboa.shape[1]
    noccb = orbob.shape[1]
    nao, nmo = mo_coeff[0].shape

    def vind(mo1):
        mo1a = mo1[:, :nocca*nmo].reshape(-1, nmo, nocca)
        mo1b = mo1[:, nocca*nmo:].reshape(-1, nmo, noccb)
        # Vectorized version: perform matrix multiplication in batch for both alpha and beta
        dm1a_intermediate = mo_coeff[0] @ mo1a @ orboa.T.conj()  # shape: (nbatch, nao, nao)
        dm1b_intermediate = mo_coeff[1] @ mo1b @ orbob.T.conj()  # shape: (nbatch, nao, nao)
        # Compute d1 - d1.conj().T for all matrices in batch
        dm1a = dm1a_intermediate - dm1a_intermediate.transpose(0, 2, 1).conj()
        dm1b = dm1b_intermediate - dm1b_intermediate.transpose(0, 2, 1).conj()
        dm1 = numpy.asarray((dm1a, dm1b))
        v1ao = vresp(dm1)
        # Vectorized version: perform matrix multiplication in batch for both alpha and beta
        v1a = mo_coeff[0].T.conj() @ v1ao[0] @ orboa  # shape: (nbatch, nmo_alpha, nocc_alpha)
        v1b = mo_coeff[1].T.conj() @ v1ao[1] @ orbob  # shape: (nbatch, nmo_beta, nocc_beta)
        v1mo = numpy.hstack((v1a.reshape(len(v1a), -1),
                             v1b.reshape(len(v1b), -1)))
        return v1mo.ravel()
    return vind


class NMR(rhf_nmr.NMR):

    def shielding(self):
        if getattr(self._scf, 'spin_square', None):
            s2 = self._scf.spin_square()[0]
            if s2 > 1e-4:
                logger.warn(self, '<S^2> = %s. UHF-NMR shielding may have large error.\n'
                            'paramagnetic NMR should include this result plus '
                            'g-tensor and HFC tensors.', s2)
        return rhf_nmr.NMR.shielding(self)

    dia = dia
    para = para
    get_fock = get_fock
    solve_mo1 = solve_mo1


scf.uhf.UHF.sNMR = lib.class_as_method(NMR)
