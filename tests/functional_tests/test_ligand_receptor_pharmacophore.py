import openpharmacophore as oph
import openpharmacophore.data as data
import nglview as nv


def test_ligand_receptor_pharmacophore_hydrogen_bonding_points():
    # We create a pharmacophore that contains only hydrogen donor and acceptor points
    pharmacophore = oph.load(data.pdb["3bbh_A_chain.pdb"])
    assert isinstance(pharmacophore, oph.LigandReceptorPharmacophore)
    # We know that the file contains a single ligand
    lig_ids = pharmacophore.receptor.find_ligands()
    assert lig_ids == ["SFG:B"]

    # We extract the pharmacophore
    pharmacophore.extract(lig_ids[0],
                          features=["hb donor", "hb acceptor"])
    assert len(pharmacophore[0]) > 0
    feat_names = [p.feat_name for p in pharmacophore[0]]
    for name in feat_names:
        assert name == "hb acceptor" or name == "hb donor"

    # Finally we visualize the pharmacophore.
    view = pharmacophore.show()
    assert view._ngl_component_names > 1


def test_ligand_receptor_pharmacophore_hydrophobic_points():
    # We create a pharmacophore that contains only hydrogen donor and acceptor points
    pharmacophore = oph.load(data.pdb["1m7w_A_chain.pdb"])
    assert isinstance(pharmacophore, oph.LigandReceptorPharmacophore)
    # We know that the file contains a single ligand
    lig_ids = pharmacophore.receptor.find_ligands()
    assert lig_ids == ["DAO:B"]

    # We know the smiles of the ligand do we pass it to the extract method
    # so, it can fix the ligand bonds and obtain an accurate pharmacophore
    smiles = "CCCCCCCCCCCC(=O)O"
    pharmacophore.extract(lig_ids[0],
                          features=["hydrophobicity"],
                          smiles=smiles)
    assert len(pharmacophore[0]) > 0
    assert all([p.feat_name == "hydrophobicity" for p in pharmacophore[0]])

    # Finally we visualize the pharmacophore.
    view = pharmacophore.show()
    assert view._ngl_component_names > 1


def test_ligand_receptor_pharmacophore_aromatic_points():
    # We create a pharmacophore that contains only aromatic points
    pharmacophore = oph.load(data.pdb["1xdn.pdb"])
    assert isinstance(pharmacophore, oph.LigandReceptorPharmacophore)
    # We know that the file contains a single ligand
    lig_ids = pharmacophore.receptor.find_ligands()
    assert lig_ids == ["ATP:B"]

    # We extract the pharmacophore
    pharmacophore.extract(lig_ids[0],
                          features=["aromatic ring"])
    assert len(pharmacophore[0]) == 1
    assert all([p.feat_name == "aromatic ring" for p in pharmacophore[0]])

    # Finally we add the pharmacophore to an existing view.
    view = nv.NGLWidget()
    n_components = len(view._ngl_component_names)
    pharmacophore.add_to_view(view)
    assert len(view._ngl_component_names) > n_components


def test_ligand_receptor_pharmacophore_from_pdb():
    # We want to create a pharmacophore for the protein-ligand complex of
    # estrogen receptor with estradiol.

    # We load a pharmacophore from a pdb file. This file contains
    # a single peptide chain with a ligand.
    pharmacophore = oph.load(data.pdb["er_alpha_A_chain.pdb"])
    assert isinstance(pharmacophore, oph.LigandReceptorPharmacophore)
    # We call find ligands method to ensure our pdb contains a single ligand.
    # We know estradiol has the id EST.
    lig_ids = pharmacophore.receptor.find_ligands()
    assert lig_ids == ["EST:B"]

    # With the full ligand id we can now extract a ligand-receptor based pharmacophore
    ligand_id = lig_ids[0]
    pharmacophore.extract(ligand_id)
    assert len(pharmacophore[0]) > 0

    # We inspect the ligand to see that it was correctly extracted. Estradiol has 20 atoms
    assert pharmacophore.ligand.GetNumAtoms == 20

    # Finally we want to view our pharmacophore using nglview
    view = pharmacophore.show()
    assert view._ngl_component_names > 1