# OpenPharmacophore
from openpharmacophore import Pharmacophore
from openpharmacophore._private_tools.exceptions import InvalidFileFormat, NoLigandsError, OpenPharmacophoreTypeError
from openpharmacophore.pharmacophore.chemical_features import PharmacophoricPointExtractor, oph_featuredefinition
from openpharmacophore.visualization.view_ligands import view_ligands
from openpharmacophore.algorithms.dbscan import dbscan_pharmacophore
from openpharmacophore.io.mol2 import load_mol2_file
from openpharmacophore.pharmacophore.color_palettes import get_color_from_palette_for_feature
# Third Party
import nglview as nv
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
# Standard Library
from collections import defaultdict
import copy
from io import BytesIO
from PIL import Image


class LigandBasedPharmacophore(Pharmacophore):
    """ Class to store and compute ligand-based pharmacophores

    Inherits from pharmacophore

    Parameters
    ----------

    elements : list of openpharmacophore.PharamacoporicPoint
        List of pharmacophoric points.

    ligands : list of rdkit.Chem.Mol
        Set of ligands from which the pharmacophore will be derived.

    feat_def : dict, optional
        A custom smarts feature definition that will be used to obtain the pharmacophoric
        points.

    Attributes
    ----------

    elements : list of openpharmacophore.PharamacophoricPoint
        List of pharmacophoric points.

    n_elements : int
        Number of pharmacophoric points.

    ligands : list of rdkit.Chem.mol
        List of ligands from which this pharmacophore was extracted.

    """

    def __init__(self, elements=[], ligands=[]):
        super().__init__(elements=elements)
        self.ligands = ligands
 
    def draw(self, n_per_row, lig_indices=None, subimage_size=(250, 200), legends=None):
        """ Get a 2D representation of the ligands with the pharmacophoric points highlighted.
            
            Parameters
            ----------
            n_per_row : int 
                Number of ligands that will be drawn in each row.
            
            lig_indices : list of int, optional
                A list with the indices of the ligands that will be drawn. If none is passed
                all ligands will be drawn.

            sub_img_size : 2-tuple of int, default=(250,200)
                The size of each subimage (each ligand drawing). The final image size may
                vary depending on the number per rows.

            legends : list of str, optional
                The legends of the ligands.

            Returns
            -------
            bytes : 
                The image in bytes. To visualize use a function such as Image from IPython.display.
        """
        if len(self.ligands) == 0:
            raise NoLigandsError("This pharmacophore contains no ligands. Cannot be drawn.")

        if not isinstance(n_per_row, int):
            raise TypeError("n_per_row must be of type int")

        if lig_indices is None:
            ligand_list = self.ligands
        else:
            ligand_list = [lig for ii, lig in enumerate(self.ligands) if ii in lig_indices]

        n_rows = len(ligand_list) // n_per_row
        if len(ligand_list) % n_per_row:
            n_rows += 1
        
        # Create a PIL image where all the individual ligand images will be combined
        n_cols = n_per_row
        img_size = (subimage_size[0] * n_cols, subimage_size[1] * n_rows)
        res = Image.new("RGB", img_size, (255, 255, 255))
        
        extractor = PharmacophoricPointExtractor()

        for ii, lig in enumerate(ligand_list):
            
            col = ii % n_per_row
            row = ii // n_per_row

            if legends:
                legend = legends[ii]
            else:
                legend = ""

            ligand = copy.deepcopy(lig)
            ligand_pharmacophore_points = extractor(ligand, 0)

            ligand.RemoveAllConformers()
            ligand = Chem.RemoveHs(ligand)

            atoms = []
            bond_colors = {}
            atom_highlights = defaultdict(list)
            highlight_radius = {}

            for point in ligand_pharmacophore_points:

                indices = point.atoms_inxs
                for idx in indices:
                    
                    atoms.append(idx)
                    atom_highlights[idx].append(get_color_from_palette_for_feature(point.feature_name))
                    highlight_radius[idx] = 0.6

                    # Draw aromatic rings bonds
                    if point.feature_name == "aromatic ring":
                        for neighbor in ligand.GetAtomWithIdx(idx).GetNeighbors():
                            nbr_idx = neighbor.GetIdx()
                            if nbr_idx not in indices:
                                continue
                            bond = ligand.GetBondBetweenAtoms(idx, nbr_idx).GetIdx()
                            bond_colors[bond] = [get_color_from_palette_for_feature("aromatic ring")]
                    
                    # If an atom has more than one feature label will contain both names
                    if idx in atoms:
                        if ligand.GetAtomWithIdx(idx).HasProp("atomNote"):
                            label = ligand.GetAtomWithIdx(idx).GetProp("atomNote")
                            label += "|" + str(point.short_name)
                        else:
                            label = point.short_name
                    else:
                        label = point.short_name

                ligand.GetAtomWithIdx(idx).SetProp("atomNote", label)

            drawing = rdMolDraw2D.MolDraw2DCairo(subimage_size[0], subimage_size[1])
            drawing.DrawMoleculeWithHighlights(ligand, legend, dict(atom_highlights), bond_colors, highlight_radius, {})
            drawing.FinishDrawing()

            png = drawing.GetDrawingText()
            bio = BytesIO(png)
            img = Image.open(bio)
            res.paste(img, box=(col * subimage_size[0], row * subimage_size[1]))

        bio = BytesIO()    
        res.save(bio, format="PNG")
        return bio.getvalue()

    @classmethod
    def single_ligand_pharmacophore(cls, ligand, radius=1.0, features=None, featdef=oph_featuredefinition()):
        """ Get a pharmacophore from a single ligand.

            Parameters
            ----------
            ligand : rdkit.chem.mol
                A ligand.
        """
        extractor = PharmacophoricPointExtractor(featdef=featdef, default_radius=radius, features=features)
        pharmacophore_points = extractor(ligand, 0)
        return cls(pharmacophore_points, [ligand])
        
    @classmethod
    def from_ligand_list(cls, ligands, method, radius=1.0, feat_list=None, feat_def=None):
        """ Class Method to derive a pharmacophore model from a list of rdkit molecules. 

        Parameters
        ----------
        ligands : list of rdkit.Chem.rdchem.Mol
            List of ligands
        
        method : str
            Name of method or algorithm to derive the ligand based pharmacophore.

        radius : float, default=1.0
            The radius in angstroms of the parmacohporic points.
        
        feat_list : list of str, optional
            List of features that will be used to derive the pharmacophore. If None is passed the
            default features will be used: donors, acceptors, aromatic rings, hydrophobics, positive
            and negative charges.
        
        feat_def : dict, optional
            Definitions of the pharmacophoric features. Dictionary which keys are SMARTS strings and 
            values are feature names. If None is passed the default rdkit definition will be used.

        Note
        -------
        Nothing is returned. The pharmacophore elements are updated with those derived from the list of ligands.
        The molecular system is updated with the set of ligands.

        """
        if not isinstance(ligands, list):
            raise OpenPharmacophoreTypeError("Ligands must be of type list")
        
        if method == "dbscan":
            points, ligands = dbscan_pharmacophore(ligands, radius=radius, feat_list=feat_list, feat_def=feat_def)
        else:
            raise NotImplementedError

        return cls(elements=points, ligands=ligands, feat_def=feat_def)

    @classmethod
    def from_ligand_file(cls, file_name, method, radius=1, feat_list=None, feat_def=None):
        """ Compute pharmacophore from a file of ligands

        Accepted file formats: smi, mol2, sdf, pdb 

        Parameters
        ----------
        file_name : str
            Name or path of the file containing the ligands.
        
        method : str
            Name of method or algorithm to compute the ligand based pharmacophore.

        radius : float, default=1.0
            The radius in angstroms of the parmacohporic points.
        
        feat_list : list of str, optional
            List of features that will be used to derive the pharmacophore. If None is passed the
            default features will be used: donors, acceptors, aromatic rings, hydrophobics, positive
            and negative charges.
        
        feat_def : dict, optional
            Definitions of the pharmacophoric features. Dictionary which keys are SMARTS strings and 
            values are feature names. If None is passed the default rdkit definition will be used.

        Note
        -------
        Nothing is returned. The pharmacophore elements are updated with those calculated from the file of ligands.
        The molecular system is updated with the set of ligands and the extractor is updated accoirding to the method used.

        """
        fextension = file_name.split(".")[-1]
        
        if fextension == "smi":
            ligands = Chem.SmilesMolSupplier(file_name, delimiter='\t', titleLine=False)
        elif fextension == "mol2":
            ligands = load_mol2_file(file_name)
        elif fextension == "sdf":
            ligands = Chem.SDMolSupplier(file_name)
        elif fextension == "pdb":
            ligands = Chem.rdmolfiles.MolFromPDBFile(file_name)
        else:
            raise InvalidFileFormat(f"{fextension} is not a supported file format")

        len(ligands)
        ligands = list(ligands)
        assert len(ligands) > 0
        tmp_pharmacophore = LigandBasedPharmacophore().from_ligand_list(
                                                        ligands=ligands, 
                                                        method=method, 
                                                        radius=radius, 
                                                        feat_list=feat_list, 
                                                        feat_def=feat_def)
        return cls(elements=tmp_pharmacophore.elements, ligands=tmp_pharmacophore.ligands, feat_def=feat_def)

    def show(self, show_ligands=True, palette="openpharmacophore"):
        """ Visualize the pharmacophore model. 

        Parameters
        ----------
        show_ligands: bool, default=True
            If true the ligands associated to the pharmacophore molecular system will be shown. 

        palette: str or dict, optional
            Color palette name or dictionary. (Default: 'openpharmacophore')

        Returns
        -------
        nglview.NGLWidget
            An nglview.NGLWidget is returned with the 'view' of the pharmacophoric model and the
            molecular system used to elucidate it.
        """

        if self.ligands and show_ligands:
            view = view_ligands(self.ligands)
        else:
            view = nv.NGLWidget()
        
        self.add_to_NGLView(view, palette=palette)

        return view

