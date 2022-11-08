from openpharmacophore import LigandBasedPharmacophore, LigandReceptorPharmacophore
import os


traj_file_formats = [
    "pdb",
    "h5",
    # TODO: add trajectory formats
]

molecular_file_formats = [
    "smi",
    "mol2",
    "sdf",
    # TODO: add other molecular formats
]


def load(pharmacophore_data):
    """ Instantiate a pharmacophore.

        Parameters
        ----------
        pharmacophore_data : Any
            Can be a file path or list of files, PDB id, or a list of molecules.

        Returns
        -------
        Pharmacophore
            Can be ligand, receptor-ligand or receptor based, depending on the type
            of input.
    """
    if os.path.isfile(pharmacophore_data):
        file_extension = pharmacophore_data.split(".")[-1]
        if file_extension in traj_file_formats:
            pharmacophore = LigandReceptorPharmacophore()
            pharmacophore.load_receptor(pharmacophore_data)
            return pharmacophore

        elif file_extension in molecular_file_formats:
            pharmacophore = LigandBasedPharmacophore()
            pharmacophore.load_ligands(pharmacophore_data)
            return pharmacophore

    raise NotImplementedError
