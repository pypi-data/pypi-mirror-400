from rdkit import Chem
from rdkit.Chem import AllChem, rdDetermineBonds
from rdkit.Chem.Draw import rdMolDraw2D


def pyscf2rdmol(pyscf_mol):
    mol_xyz = pyscf_mol.tostring(format="xyz")
    raw_mol = Chem.MolFromXYZBlock(mol_xyz)
    rd_mol = Chem.Mol(raw_mol)
    rdDetermineBonds.DetermineBonds(rd_mol, charge=pyscf_mol.charge)
    return rd_mol


def draw_rdmol_with_label(rd_mol, labels, filename, to2D=True):
    mol_to_draw = Chem.Mol(rd_mol)
    for atom_id, label in labels.items():
        atom = mol_to_draw.GetAtomWithIdx(atom_id)
        atom.SetProp("atomNote", label)
    if to2D:
        mol_to_draw.RemoveAllConformers()
        AllChem.Compute2DCoords(mol_to_draw)
    drawer = rdMolDraw2D.MolDraw2DCairo(600, 600)
    drawer.DrawMolecule(mol_to_draw)
    drawer.FinishDrawing()
    drawer.WriteDrawingText(filename)
