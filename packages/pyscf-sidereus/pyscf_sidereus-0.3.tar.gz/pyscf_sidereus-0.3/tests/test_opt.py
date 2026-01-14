import pyscf
import pyscf.sidereus


class TestMINOPT:
    def setup_method(self, method):
        self.atom = "H 0 0 0; H 0 0 1"
        self.basis = "sto-3g"
        self.xc = "LDA"

    def test_rhf(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.RHF().sOPT().kernel()

    def test_rks(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.RKS(xc=self.xc).sOPT().kernel()

    def test_uhf(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.UHF().sOPT().kernel()

    def test_uks(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.UKS(xc=self.xc).sOPT().kernel()


class TestTSOPT:
    def setup_method(self, method):
        self.atom = """
N           0.00083273        0.00057666       -0.00069428
H           1.00555992       -0.00091855       -0.00131155
H          -0.50382419        0.86943925        0.00002190
H          -0.50256846       -0.86909736        0.00198393
"""
        self.basis = "sto-3g"
        self.xc = "LDA"

    def test_rhf(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.RHF().sOPT(ts=True).kernel()

    def test_rks(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.RKS(xc=self.xc).sOPT(ts=True).kernel()

    def test_uhf(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.UHF().sOPT(ts=True).kernel()

    def test_uks(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.UKS(xc=self.xc).sOPT(ts=True).kernel()


class TestTSSearch:
    def setup_method(self, method):
        self.product_xyzs = """4

  N    -0.00000000     0.00000000     0.07558051
  H     0.94112550     0.00000000    -0.35009807
  H    -0.47056275     0.81503859    -0.35009807
  H    -0.47056275    -0.81503859    -0.35009807
"""

        self.atom = """
  N    -0.00000000     0.00000000    -0.07558051
  H     0.94112550     0.00000000     0.35009807
  H    -0.47056275     0.81503859     0.35009807
  H    -0.47056275    -0.81503859     0.35009807
"""
        self.basis = "sto-3g"
        self.xc = "LDA"

    def test_rhf(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.RHF().sOPT(ts=True, product_xyzs=self.product_xyzs).kernel()

    def test_rks(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.RKS(xc=self.xc).sOPT(
            ts=True, product_xyzs=self.product_xyzs).kernel()

    def test_uhf(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.UHF().sOPT(ts=True, product_xyzs=self.product_xyzs).kernel()

    def test_uks(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.UKS(xc=self.xc).sOPT(
            ts=True, product_xyzs=self.product_xyzs).kernel()
