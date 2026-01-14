# Copyright 2014-2022 The PySCF Developers, 2025-2026 Sidereus-AI ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");


from pyscf import scf
import numpy
from pyscf import lib
from pyscf.lib import logger
from pyscf.scf import _vhf
from pyscf.scf import cphf
from pyscf.scf import _response_functions  # noqa
from pyscf.data import nist
from ..utils.rdkit import pyscf2rdmol, draw_rdmol_with_label, Chem
from ..utils.matplotlib import plot_spectrum


def dia(nmrobj, shielding_nuc=None, dm0=None):
    '''Diamagnetic part of NMR shielding tensors.

    See also J. Olsen et al., Theor. Chem. Acc., 90, 421 (1995)
    '''
    if shielding_nuc is None:
        shielding_nuc = nmrobj.shielding_nuc
    if dm0 is None:
        dm0 = nmrobj._scf.make_rdm1()

    mol = nmrobj.mol
    mf = nmrobj._scf

    if getattr(mf, 'with_x2c', None):
        raise NotImplementedError('X2C for NMR shielding')

    if getattr(mf, 'with_qmmm', None):
        raise NotImplementedError('NMR shielding with QM/MM')

    if getattr(mf, 'with_solvent', None):
        raise NotImplementedError('NMR shielding with Solvent')

    msc_dia = []
    for n, atm_id in enumerate(shielding_nuc):
        with mol.with_rinv_origin(mol.atom_coord(atm_id)):
            # a11part = (B dot) -1/2 frac{\vec{r}_N}{r_N^3} r (dot mu)
            h11 = mol.intor('int1e_giao_a11part', comp=9)
            e11 = numpy.einsum('xij,ij->x', h11, dm0).reshape(3, 3)
            e11 = e11 - numpy.eye(3) * e11.trace()
            h11 = mol.intor('int1e_a01gp', comp=9)
            e11 += numpy.einsum('xij,ij->x', h11, dm0).reshape(3, 3)
        msc_dia.append(e11)
    return numpy.array(msc_dia).reshape(-1, 3, 3)


def para(nmrobj, mo10=None, mo_coeff=None, mo_occ=None, shielding_nuc=None):
    '''Paramagnetic part of NMR shielding tensors.
    '''
    if mo_coeff is None:
        mo_coeff = nmrobj._scf.mo_coeff
    if mo_occ is None:
        mo_occ = nmrobj._scf.mo_occ
    if shielding_nuc is None:
        shielding_nuc = nmrobj.shielding_nuc
    if mo10 is None:
        mo10 = nmrobj.solve_mo1()[0]

    mol = nmrobj.mol
    para_vir = numpy.empty((len(shielding_nuc), 3, 3))
    para_occ = numpy.empty((len(shielding_nuc), 3, 3))
    occidx = mo_occ > 0
    viridx = mo_occ == 0
    orbo = mo_coeff[:, occidx]
    orbv = mo_coeff[:, viridx]
    # *2 for double occupancy
    # Vectorized version: extract occupied and virtual parts and perform matrix multiplication in batch
    mo10_occ = mo10[:, occidx, :]  # shape: (3, nocc, nocc)
    mo10_vir = mo10[:, viridx, :]  # shape: (3, nvir, nocc)
    dm10_oo = orbo @ (mo10_occ*2) @ orbo.T.conj()  # shape: (3, nao, nao)
    dm10_vo = orbv @ (mo10_vir*2) @ orbo.T.conj()  # shape: (3, nao, nao)
    for n, atm_id in enumerate(shielding_nuc):
        mol.set_rinv_origin(mol.atom_coord(atm_id))
        # H^{01} = 1/2(A01 dot p + p dot A01) => (a01p + c.c.)/2 ~ <a01p>
        # Im[A01 dot p] = Im[vec{r}/r^3 x vec{p}] = Im[-i p (1/r) x p] = -p (1/r) x p
        h01i = mol.intor_asymmetric('int1e_prinvxp', 3)  # = -Im[H^{01}]
        # <H^{01},MO^1> = - Tr(Im[H^{01}],Im[MO^1]) = Tr(-Im[H^{01}],Im[MO^1])
        # *2 for + c.c.
        para_occ[n] = numpy.einsum('xji,yij->xy', dm10_oo, h01i) * 2
        # *2 for + c.c.
        para_vir[n] = numpy.einsum('xji,yij->xy', dm10_vo, h01i) * 2
    msc_para = para_occ + para_vir
    return msc_para, para_vir, para_occ


def make_h10(mol, dm0, verbose=logger.WARN):
    '''Imaginary part of first order Fock operator

    Note the side effects of set_common_origin
    '''
    log = logger.new_logger(mol, verbose)
    # A10_i dot p + p dot A10_i consistents with <p^2 g>
    # A10_j dot p + p dot A10_j consistents with <g p^2>
    # 1/2(A10_j dot p + p dot A10_j) => Im[1/4 (rjxp - pxrj)] = -1/2 <irjxp>
    log.debug('First-order GIAO Fock matrix')
    h1 = -.5 * mol.intor('int1e_giao_irjxp', 3) + make_h10giao(mol, dm0)
    return h1


def get_jk(mol, dm0):
    # J = Im[(i i|\mu g\nu) + (i gi|\mu \nu)] = -i (i i|\mu g\nu)
    # K = Im[(\mu gi|i \nu) + (\mu i|i g\nu)]
    #   = [-i (\mu g i|i \nu)] - h.c.   (-h.c. for anti-symm because of the factor -i)
    intor = mol._add_suffix('int2e_ig1')
    vj, vk = _vhf.direct_mapdm(intor,  # (g i,j|k,l)
                               'a4ij', ('lk->s1ij', 'jk->s1il'),
                               dm0, 3,  # xyz, 3 components
                               mol._atm, mol._bas, mol._env)
    vk = vk - numpy.swapaxes(vk, -1, -2)
    return -vj, -vk


def make_h10giao(mol, dm0):
    vj, vk = get_jk(mol, dm0)
    h1 = vj - .5 * vk
    # Im[<g\mu|H|g\nu>] = -i * (gnuc + gkin)
    h1 -= mol.intor_asymmetric('int1e_ignuc', 3)
    if mol.has_ecp():
        h1 -= mol.intor_asymmetric('ECPscalar_ignuc', 3)
    h1 -= mol.intor('int1e_igkin', 3)
    return h1


def make_s10(mol):
    '''First order overlap matrix wrt external magnetic field.'''
    # Im[<g\mu |g\nu>]
    s1 = -mol.intor_asymmetric('int1e_igovlp', 3)
    return s1


get_ovlp = make_s10


def solve_mo1(nmrobj, mo_energy=None, mo_coeff=None, mo_occ=None,
              h1=None, s1=None):
    '''Solve the first order equation'''
    if mo_energy is None:
        mo_energy = nmrobj._scf.mo_energy
    if mo_coeff is None:
        mo_coeff = nmrobj._scf.mo_coeff
    if mo_occ is None:
        mo_occ = nmrobj._scf.mo_occ

    cput1 = (logger.process_clock(), logger.perf_counter())
    log = logger.Logger(nmrobj.stdout, nmrobj.verbose)

    mol = nmrobj.mol
    orbo = mo_coeff[:, mo_occ > 0]
    if h1 is None:
        dm0 = nmrobj._scf.make_rdm1(mo_coeff, mo_occ)
        h1 = lib.einsum('xpq,pi,qj->xij', nmrobj.get_fock(dm0),
                        mo_coeff.conj(), orbo)
        cput1 = log.timer('first order Fock matrix', *cput1)
    if s1 is None:
        s1 = lib.einsum('xpq,pi,qj->xij', nmrobj.get_ovlp(mol),
                        mo_coeff.conj(), orbo)

    # Always use CPHF
    vind = gen_vind(nmrobj._scf, mo_coeff, mo_occ)
    mo10, mo_e10 = cphf.solve(vind, mo_energy, mo_occ, h1, s1,
                              nmrobj.max_cycle_cphf, nmrobj.conv_tol,
                              verbose=log)

    log.timer('solving mo1 eqn', *cput1)
    return mo10, mo_e10


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


def gen_vind(mf, mo_coeff, mo_occ):
    '''Induced potential'''
    vresp = mf.gen_response(singlet=True, hermi=2)
    occidx = mo_occ > 0
    orbo = mo_coeff[:, occidx]
    nocc = orbo.shape[1]
    nao, nmo = mo_coeff.shape

    def vind(mo1):
        # Vectorized version: perform matrix multiplication in batch
        mo1_batch = mo1.reshape(-1, nmo, nocc)
        # shape: (nbatch, nao, nao)
        dm1_intermediate = mo_coeff @ (mo1_batch*2) @ orbo.T.conj()
        # Compute d1 - d1.conj().T for all matrices in batch
        dm1 = dm1_intermediate - dm1_intermediate.transpose(0, 2, 1).conj()
        v1mo = lib.einsum('xpq,pi,qj->xij', vresp(dm1), mo_coeff.conj(), orbo)
        return v1mo.ravel()
    return vind


class NMR(lib.StreamObject):
    def __init__(self, scf_method, element="H"):
        self.mol = scf_method.mol
        self.verbose = scf_method.mol.verbose
        self.stdout = scf_method.mol.stdout
        self.chkfile = scf_method.chkfile
        self._scf = scf_method

        self.element = element
        if element is None:
            self.shielding_nuc = range(self.mol.natm)
        else:
            self.shielding_nuc = [i for i in range(self.mol.natm)
                                  if self.mol.atom_symbol(i) == element]
        self.max_cycle_cphf = 20
        self.conv_tol = 1e-9

        self.B = NotImplemented

        self._keys = set(self.__dict__.keys())

    def dump_flags(self, verbose=None):
        log = logger.new_logger(self, verbose)
        log.info('\n')
        log.info('******** %s for %s ********',
                 self.__class__, self._scf.__class__)
        log.info('gauge = GIAO')
        log.info('shielding for atoms %s', str(self.shielding_nuc))
        log.info('Solving MO10 eq with CPHF.')
        log.info('CPHF conv_tol = %g', self.conv_tol)
        log.info('CPHF max_cycle_cphf = %d', self.max_cycle_cphf)
        if not self._scf.converged:
            log.warn('Ground state SCF is not converged')
        return self

    # Note mo10 is the imaginary part of MO^1
    def kernel(self):
        if self._scf.__module__.startswith("gpu4pyscf"):
            self.gpu_shielding()
        else:
            self.shielding()
        return self.B

    def summary(self, B=None, w=None, avg_equiv=True, img=None, spectrum=None):
        # http://cheshirenmr.info/ScalingFactors.htm
        # from Lodewyk, M. W.; Siebert, M. R.; Tantillo, D. J. Chem. Rev. 2012, 112, 1839-1862.
        # Only for b3lyp/6-31G* and SMD(Chloroform) or gas
        if B is None:
            B = self.B
        with_solvent = getattr(self._scf, 'with_solvent', None)
        slopes = numpy.empty(len(self.shielding_nuc))
        intercepts = numpy.empty(len(self.shielding_nuc))
        for n, atom_id in enumerate(self.shielding_nuc):
            element = self.mol.atom_symbol(atom_id)
            if element == "H":
                slopes[n] = 1.0 / 0.9957
                intercepts[n] = 32.2884
            elif element == "C":
                slopes[n] = 1.0 / 0.9269
                intercepts[n] = 187.4743
            else:
                raise NotImplementedError(f"Scaling for {element}")
        b_iso = numpy.trace(B, axis1=-2, axis2=-1) / 3
        shifts = (intercepts - b_iso) * slopes
        if avg_equiv or img:
            rd_mol = pyscf2rdmol(self.mol)
        if avg_equiv:
            ranks = list(Chem.CanonicalRankAtoms(rd_mol, breakTies=False))
            new_shifts = numpy.copy(shifts)
            for i in range(len(self.shielding_nuc)):
                curr_atom_idx = self.shielding_nuc[i]
                curr_rank = ranks[curr_atom_idx]
                equiv_indices = [j for j, idx in enumerate(self.shielding_nuc)
                                 if ranks[idx] == curr_rank]
                if len(equiv_indices) > 1:
                    avg_val = numpy.mean(shifts[equiv_indices])
                    new_shifts[i] = avg_val
            shifts = new_shifts
        if img:
            labels = {
                j: f"{shifts[i]:.2f}"
                for i, j in enumerate(self.shielding_nuc)
            }
            draw_rdmol_with_label(rd_mol, labels, img)
        if spectrum:
            if self.element == "H":
                default_min = 0
                default_max = 13
                default_pad = 1
                default_lw = 0.1
            elif self.element == "C":
                default_min = 0
                default_max = 210
                default_pad = 10
                default_lw = 2.0
            x_min = min(min(shifts), default_min) - default_pad
            x_max = max(max(shifts), default_max) + default_pad
            lw = default_lw if w is None else w
            fig, ax, ax2 = plot_spectrum(shifts,
                                         width=lw,
                                         x_min=x_min,
                                         x_max=x_max,
                                         x_label='Chemical Shift (ppm)',
                                         y_label='Intensity',
                                         y2_label="Occupancy",
                                         y_legend="Simulated Spectrum",
                                         y2_legend="Stick Spectrum")
            ticks = ax2.get_yticks()
            ax2.set_yticks([t for t in ticks if t >= 0 and t == int(t)])
            ax.invert_xaxis()
            ax.set_yticklabels([])
            fig.savefig(spectrum)
            fig.clf()
        log = logger.new_logger(self, 2)
        log.log(
            "---------------------------------\n"
            " atom      Chemical Shift        \n"
            "   #         ppm                 \n"
            "---------------------------------")
        for i, atm_id in enumerate(self.shielding_nuc):
            log.log("%5d   %12.4f             " % (i, shifts[i]))
        log.log("---------------------------------\n")
        return shifts

    def shielding(self):
        cput0 = (logger.process_clock(), logger.perf_counter())
        self.check_sanity()
        self.dump_flags()

        unit_ppm = nist.ALPHA**2 * 1e6
        msc_dia = self.dia()

        mo10, mo_e10 = self.solve_mo1()
        msc_para, para_vir, para_occ = self.para(mo10=mo10)

        msc_dia *= unit_ppm
        msc_para *= unit_ppm
        para_vir *= unit_ppm
        para_occ *= unit_ppm
        msc_dia = numpy.round(msc_dia, decimals=4)
        msc_para = numpy.round(msc_para, decimals=4)
        e11 = numpy.round(msc_para + msc_dia, decimals=4)

        logger.timer(self, 'NMR shielding', *cput0)
        if self.verbose >= logger.NOTE:
            for i, atm_id in enumerate(self.shielding_nuc):
                _write(self.stdout, e11[i],
                       '\ntotal shielding of atom %d %s'
                       % (atm_id, self.mol.atom_symbol(atm_id)))
                _write(self.stdout, msc_dia[i], 'dia-magnetic contribution')
                _write(self.stdout, msc_para[i], 'para-magnetic contribution')
                if self.verbose >= logger.INFO:
                    _write(self.stdout, para_occ[i],
                           'occ part of para-magnetism')
                    _write(self.stdout, para_vir[i],
                           'vir part of para-magnetism')
        self.B = e11
        return e11

    def gpu_shielding(self):
        from gpu4pyscf.properties.shielding import eval_shielding
        msc_dia, msc_para = eval_shielding(self._scf)
        msc_para = numpy.round(msc_para[self.shielding_nuc], decimals=4)
        msc_dia = numpy.round(msc_dia[self.shielding_nuc], decimals=4)
        e11 = numpy.round(msc_para + msc_dia, decimals=4)
        self.B = e11.get()
        if self.verbose >= logger.NOTE:
            for i, atm_id in enumerate(self.shielding_nuc):
                _write(self.stdout, e11[i],
                       '\ntotal shielding of atom %d %s'
                       % (atm_id, self.mol.atom_symbol(atm_id)))
                _write(self.stdout, msc_dia[i],
                       'dia-magnetic contribution')
                _write(self.stdout, msc_para[i],
                       'para-magnetic contribution')

    dia = dia
    para = para
    get_fock = get_fock
    solve_mo1 = solve_mo1

    def get_ovlp(self, mol=None):
        if mol is None:
            mol = self.mol
        return get_ovlp(mol)


def _write(stdout, msc3x3, title):
    stdout.write('%s\n' % title)
    stdout.write('B_x %s\n' % str(msc3x3[0]))
    stdout.write('B_y %s\n' % str(msc3x3[1]))
    stdout.write('B_z %s\n' % str(msc3x3[2]))
    stdout.flush()


scf.hf.RHF.sNMR = lib.class_as_method(NMR)
