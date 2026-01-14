# Copyright 2014-2022 The PySCF Developers, 2025-2026 Sidereus-AI ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");


from pyscf import dft
import numpy
from pyscf import lib
from pyscf.lib import logger
from pyscf.scf import _vhf
from pyscf.dft import numint
from . import rhf as rhf_nmr
from . import rks as rks_nmr
from . import uhf as uhf_nmr


def get_vxc_giao(ni, mol, grids, xc_code, dms, max_memory=2000, verbose=None):
    xctype = ni._xc_type(xc_code)
    make_rho, nset, nao = ni._gen_rho_evaluator(mol, dms, hermi=1)
    ngrids = len(grids.weights)
    BLKSIZE = numint.BLKSIZE
    blksize = int(max_memory*1e6/(12*nao*8*BLKSIZE))
    blksize = max(4, min(blksize, ngrids//BLKSIZE+1, 1200)) * BLKSIZE
    shls_slice = (0, mol.nbas)
    ao_loc = mol.ao_loc_nr()

    vmat = numpy.zeros((2, 3, nao, nao))
    if xctype == 'LDA':
        buf = numpy.empty((4, blksize, nao))
        ao_deriv = 0
        for ao, mask, weight, coords \
                in ni.block_loop(mol, grids, nao, ao_deriv, max_memory,
                                 blksize=blksize, buf=buf):
            rho_a = make_rho(0, ao, mask, 'LDA')
            rho_b = make_rho(1, ao, mask, 'LDA')
            vxc = ni.eval_xc(xc_code, (rho_a, rho_b), 1, deriv=1)[1]
            vrho = vxc[0]
            giao = mol.eval_gto('GTOval_ig', coords, comp=3,
                                non0tab=mask, out=buf[1:])
            aow = numpy.einsum('pi,p->pi', ao, weight*vrho[:, 0])
            vmat[0, 0] += numint._dot_ao_ao(mol, aow,
                                            giao[0], mask, shls_slice, ao_loc)
            vmat[0, 1] += numint._dot_ao_ao(mol, aow,
                                            giao[1], mask, shls_slice, ao_loc)
            vmat[0, 2] += numint._dot_ao_ao(mol, aow,
                                            giao[2], mask, shls_slice, ao_loc)
            aow = numpy.einsum('pi,p->pi', ao, weight*vrho[:, 1])
            vmat[1, 0] += numint._dot_ao_ao(mol, aow,
                                            giao[0], mask, shls_slice, ao_loc)
            vmat[1, 1] += numint._dot_ao_ao(mol, aow,
                                            giao[1], mask, shls_slice, ao_loc)
            vmat[1, 2] += numint._dot_ao_ao(mol, aow,
                                            giao[2], mask, shls_slice, ao_loc)
            vxc = vrho = aow = None

    elif xctype == 'GGA':
        buf = numpy.empty((10, blksize, nao))
        ao_deriv = 1
        for ao, mask, weight, coords \
                in ni.block_loop(mol, grids, nao, ao_deriv, max_memory,
                                 blksize=blksize, buf=buf):
            rho_a = make_rho(0, ao, mask, 'GGA')
            rho_b = make_rho(1, ao, mask, 'GGA')
            vxc = ni.eval_xc(xc_code, (rho_a, rho_b), 1, deriv=1)[1]
            vrho, vsigma = vxc[:2]
            giao = mol.eval_gto('GTOval_ig', coords, 3,
                                non0tab=mask, out=buf[4:])

            wva = numpy.empty_like(rho_a)
            wva[0] = weight * vrho[:, 0]
            wva[1:] = rho_a[1:] * (weight * vsigma[:, 0] * 2)  # sigma_uu
            wva[1:] += rho_b[1:] * (weight * vsigma[:, 1])      # sigma_ud
            wvb = numpy.empty_like(rho_b)
            wvb[0] = weight * vrho[:, 1]
            wvb[1:] = rho_b[1:] * (weight * vsigma[:, 2] * 2)  # sigma_dd
            wvb[1:] += rho_a[1:] * (weight * vsigma[:, 1])      # sigma_ud

            aow = numpy.einsum('npi,np->pi', ao[:4], wva)
            vmat[0, 0] += numint._dot_ao_ao(mol, aow,
                                            giao[0], mask, shls_slice, ao_loc)
            vmat[0, 1] += numint._dot_ao_ao(mol, aow,
                                            giao[1], mask, shls_slice, ao_loc)
            vmat[0, 2] += numint._dot_ao_ao(mol, aow,
                                            giao[2], mask, shls_slice, ao_loc)
            aow = numpy.einsum('npi,np->pi', ao[:4], wvb)
            vmat[1, 0] += numint._dot_ao_ao(mol, aow,
                                            giao[0], mask, shls_slice, ao_loc)
            vmat[1, 1] += numint._dot_ao_ao(mol, aow,
                                            giao[1], mask, shls_slice, ao_loc)
            vmat[1, 2] += numint._dot_ao_ao(mol, aow,
                                            giao[2], mask, shls_slice, ao_loc)

            giao = mol.eval_gto('GTOval_ipig', coords, 9,
                                non0tab=mask, out=buf[1:])
            rks_nmr._gga_sum_(vmat[0], mol, ao, giao,
                              wva, mask, shls_slice, ao_loc)
            rks_nmr._gga_sum_(vmat[1], mol, ao, giao,
                              wvb, mask, shls_slice, ao_loc)
            vxc = vrho = vsigma = aow = None
    elif xctype == 'MGGA':
        raise NotImplementedError('meta-GGA')

    return vmat - vmat.transpose(0, 1, 3, 2)


def get_fock(nmrobj, dm0=None):
    '''First order Fock matrix wrt external magnetic field'''
    if dm0 is None:
        dm0 = nmrobj._scf.make_rdm1()

    mol = nmrobj.mol

    log = logger.Logger(nmrobj.stdout, nmrobj.verbose)
    log.debug('First-order GIAO Fock matrix')

    mf = nmrobj._scf
    ni = mf._numint
    omega, alpha, hyb = ni.rsh_and_hybrid_coeff(mf.xc, spin=mol.spin)

    mem_now = lib.current_memory()[0]
    max_memory = max(2000, mf.max_memory*.9-mem_now)
    # Attach mo_coeff and mo_occ to improve get_vxc_giao efficiency
    dm0 = lib.tag_array(dm0, mo_coeff=mf.mo_coeff, mo_occ=mf.mo_occ)
    h1 = -get_vxc_giao(ni, mol, mf.grids, mf.xc, dm0,
                       max_memory=max_memory, verbose=nmrobj.verbose)

    intor = mol._add_suffix('int2e_ig1')
    if abs(hyb) > 1e-10:
        vj, vk = rhf_nmr.get_jk(mol, dm0)
        h1 += vj[0] + vj[1] - hyb * vk
        if abs(omega) > 1e-10:
            with mol.with_range_coulomb(omega):
                h1 -= (alpha-hyb) * rhf_nmr.get_jk(mol, dm0)[1]
    else:
        vj = _vhf.direct_mapdm(intor, 'a4ij', 'lk->s1ij',
                               dm0, 3, mol._atm, mol._bas, mol._env)
        h1 -= vj[0] + vj[1]

    h1 -= .5 * mol.intor('int1e_giao_irjxp', 3)
    h1 -= mol.intor_asymmetric('int1e_ignuc', 3)
    if mol.has_ecp():
        h1 -= mol.intor_asymmetric('ECPscalar_ignuc', 3)
    h1 -= mol.intor('int1e_igkin', 3)

    if nmrobj.chkfile:
        lib.chkfile.dump(nmrobj.chkfile, 'nmr/h1', h1)
    return h1


def solve_mo1(nmrobj, mo_energy=None, mo_coeff=None, mo_occ=None,
              h1=None, s1=None):
    # Only use CPHF for hybrid functionals - but now always use CPHF
    # Call the parent function (which always uses CPHF)
    return uhf_nmr.solve_mo1(nmrobj, mo_energy, mo_coeff, mo_occ,
                             h1, s1)


class NMR(uhf_nmr.NMR):
    get_fock = get_fock
    solve_mo1 = solve_mo1


dft.uks.UKS.sNMR = dft.uks_symm.UKS.sNMR = lib.class_as_method(NMR)
