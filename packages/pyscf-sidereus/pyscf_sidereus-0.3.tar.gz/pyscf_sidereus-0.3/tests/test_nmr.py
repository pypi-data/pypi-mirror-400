import pyscf
import pyscf.sidereus


class TestNMR:
    def setup_method(self, method):
        self.atom = 'H 0 0 0; F 0 0 0.917'
        self.basis = 'sto-3g'
        self.xc = "LDA"

    def test_rhf(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.RHF().run().sNMR().kernel()

    def test_uhf(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.UHF().run().sNMR().kernel()

    def test_rks(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.RKS(xc=self.xc).run().sNMR().kernel()

    def test_uks(self):
        mol = pyscf.M(atom=self.atom, basis=self.basis)
        mol.UKS(xc=self.xc).run().sNMR().kernel()
