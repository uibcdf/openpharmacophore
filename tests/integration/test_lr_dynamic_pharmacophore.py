import openpharmacophore as oph
from assert_view import assert_view_contains_pharmacophore


def test_dynamic_ligand_receptor_pharmacophore(traj_er_alpha):
    # We obtain pharmacophores from a md trajectory of er-alpha
    # that consists of three frames
    protein = oph.load(traj_er_alpha)
    # We know that the file contains a single ligand
    assert protein.has_ligands()
    # The receptor already contains hydrogens
    assert protein.has_hydrogens()

    lig_ids = protein.ligand_ids()
    assert len(lig_ids) == 1

    ligand = protein.get_ligand()
    ligand.fix_bond_order(
        smiles="C[C@]12CC[C@@H]3c4ccc(cc4CC[C@H]3[C@@H]1CC[C@@H]2O)O"
    )
    ligand.add_hydrogens()
    assert ligand.n_atoms == 44

    binding_site = protein.extract_binding_site(ligand=ligand)

    # We extract the pharmacophore
    pharmacophore = oph.LigandReceptorPharmacophore(ligand, binding_site)
    pharmacophore.extract(frames=[0, 1, 2])
    assert len(pharmacophore) == 3
    assert len(pharmacophore[0]) > 0
    assert len(pharmacophore[1]) > 0
    assert len(pharmacophore[2]) > 0

    # We inspect the ligand to see that it was correctly extracted. It should
    # have hydrogens, because the receptor has too
    assert pharmacophore.receptor.ligand.GetNumAtoms() == 44

    # We create a view of the second frame
    viewer = oph.Viewer(protein=protein, ligand=ligand)
    view = viewer.show(frame=1)