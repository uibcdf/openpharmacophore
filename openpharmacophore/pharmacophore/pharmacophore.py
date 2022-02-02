# OpenPharmacophore
from openpharmacophore._private_tools.exceptions import InvalidFeatureError, InvalidFileFormat
from openpharmacophore.io import (from_pharmer, from_moe, from_ligandscout,
 to_ligandscout, to_moe, to_pharmagist, to_pharmer)
from openpharmacophore import PharmacophoricPoint
from openpharmacophore.algorithms.discretize import discretize
from openpharmacophore.pharmacophore.pharmacophoric_point import distance_bewteen_pharmacophoric_points
from openpharmacophore.pharmacophore.color_palettes import get_color_from_palette_for_feature
# Third party
import networkx as nx
import nglview as nv
import numpy as np
import pyunitwizard as puw
from rdkit import Geometry, RDLogger
from rdkit.Chem import ChemicalFeatures
from rdkit.Chem.Pharm3D import Pharmacophore as rdkitPharmacophore
RDLogger.DisableLog('rdApp.*') # Disable rdkit warnings
# Standard library
import copy
import itertools

class Pharmacophore():
    """ Native object for pharmacophores.

    Openpharmacophore native class to store pharmacophoric models. A pharmacophore can be constructed 
    from a list of pharmacophoric_points or from a file.

    Parameters
    ----------

    pharmacophoric_points : list openpharmacophore.PharmacophoricPoint
        List of pharmacophoric points

    Attributes
    ----------

    pharmacophoric_points : list openpharmacophore.PharmacophoricPoint
        List of pharmacophoric pharmacophoric_points

    n_pharmacophoric_points : int
        Number of pharmacophoric points

    """
    def __init__(self, pharmacophoric_points=[]):

        self.pharmacophoric_points = pharmacophoric_points
        self.n_pharmacophoric_points = len(pharmacophoric_points)
    
    @classmethod
    def from_file(cls, file_name, **kwargs):
        """
        Class method to load a pharmacophore from a file.

        Parameters
        ---------
        file_name : str
            Name of the file containing the pharmacophore

        """
        fextension = file_name.split(".")[-1]
        if fextension == "json":
            points, _ , _ = from_pharmer(file_name, False)

        elif fextension == "ph4":
            points = from_moe(file_name)
           
        elif fextension == "pml":
            points = from_ligandscout(file_name)
        
        else:
            raise InvalidFileFormat(f"Invalid file format, \"{file_name}\" is not a supported file format")
        
        return cls(pharmacophoric_points=points)    
        
    def add_to_NGLView(self, view, palette='openpharmacophore'):
        """Add the pharmacophore representation to a view (NGLWidget) from NGLView.

        Each pharmacophoric element is added to the NGLWidget as a new component.

        Parameters
        ----------
        view : nglview.NGLWidget
            View as NGLView widget where the representation of the pharmacophore is going to be
            added.
        palette : str or dict
            Color palette name or dictionary. (Default: 'openpharmacophore')

        Note
        ----
        Nothing is returned. The `view` object is modified in place.
        """
        first_element_index = len(view._ngl_component_ids)
        for ii, element in enumerate(self.pharmacophoric_points):
            # Add Spheres
            center = puw.get_value(element.center, to_unit="angstroms").tolist()
            radius = puw.get_value(element.radius, to_unit="angstroms")
            feature_color = get_color_from_palette_for_feature(element.feature_name, color_palette=palette)
            label = f"{element.feature_name}_{ii}"
            view.shape.add_sphere(center, feature_color, radius, label)

            # Add vectors
            if element.has_direction:
                label = f"{element.feature_name}_vector"
                if element.feature_name == "hb acceptor":
                    end_arrow = puw.get_value(element.center - 2 * radius * puw.quantity(element.direction, "angstroms"), to_unit='angstroms').tolist()
                    view.shape.add_arrow(end_arrow, center, feature_color, 0.2, label)
                else:
                    end_arrow = puw.get_value(element.center + 2 * radius * puw.quantity(element.direction, "angstroms"), to_unit='angstroms').tolist()
                    view.shape.add_arrow(center, end_arrow, feature_color, 0.2, label)
        
        # Add opacity to spheres
        last_element_index = len(view._ngl_component_ids)
        for jj in range(first_element_index, last_element_index):
            view.update_representation(component=jj, opacity=0.8)

    def show(self, palette='openpharmacophore'):
        """ Show the pharmacophore model.

        Parameters
        ----------
        palette : str or dict.
            Color palette name or dictionary. (Default: 'openpharmacophore')

        Returns
        -------
        nglview.NGLWidget
            An nglview.NGLWidget is returned with the 'view' of the pharmacophoric model and the
            molecular system used to elucidate it.

        """

        view = nv.NGLWidget()
        self.add_to_NGLView(view, palette=palette)

        return view

    def add_element(self, pharmacophoric_point):
        """Add a new element to the pharmacophore in an ordered manner. pharmacophoric_points of the 
           pharmacophore are sorted by feature type.

        Parameters
        ----------
        pharmacophoric_point : openpharmacophore.PharmacophricPoint
            The pharmacophoric point that will be added.

        Note
        ------
            The pharmacophoric element given as input argument is added to the pharmacophore
            as a new entry of the list `pharmacophoric_points`.

        """
        # bisect.insort(self.pharmacophoric_points, pharmacophoric_point, key=lambda p : p.short_name)
        self.pharmacophoric_points.append(pharmacophoric_point)
        self.n_pharmacophoric_points +=1
    
    def remove_pharmacophoric_points(self, element_indices):
        """ Remove pharmacophoric_points from the pharmacophore.

        Parameters
        ----------
        element_indices : int or list of int
            Indices of the pharmacophoric_points to be removed. Can be a list of integers if multiple pharmacophoric_points will be
            removed or a single integer to remove one element.

        Note
        -----
            The pharmacophoric element given as input argument is removed from the pharmacophore.
        """
        if isinstance(element_indices, int):
            self.pharmacophoric_points.pop(element_indices)
            self.n_pharmacophoric_points -=1
        elif isinstance(element_indices, list):
            new_pharmacophoric_points = [element for i, element in enumerate(self.pharmacophoric_points) if i not in element_indices]
            self.pharmacophoric_points = new_pharmacophoric_points
            self.n_pharmacophoric_points = len(self.pharmacophoric_points)

    def remove_feature(self, feat_type):
        """ Remove an especific feature type from the pharmacophore pharmacophoric_points list

        Parameters
        ----------
        feat_type : str
            Name or type of the feature to be removed.

        Note
        -----
            The pharmacophoric pharmacophoric_points of the feature type given as input argument 
            are removed from the pharmacophore.
        """
        feats = PharmacophoricPoint.get_valid_features()
        if feat_type not in feats:
            raise InvalidFeatureError(f"Cannot remove feature. \"{feat_type}\" is not a valid feature type")

        temp_pharmacophoric_points = [element for element in self.pharmacophoric_points if element.feature_name != feat_type]
        if len(temp_pharmacophoric_points) == self.n_pharmacophoric_points: # No element was removed
            raise InvalidFeatureError(f"Cannot remove feature. The pharmacophore does not contain any {feat_type}")
        self.pharmacophoric_points = temp_pharmacophoric_points
        self.n_pharmacophoric_points = len(self.pharmacophoric_points)
    
    def _reset(self):
        """Private method to reset all attributes to default values.

        Note
        ----
        Nothing is returned. All attributes are set to default values.
        """
        self.pharmacophoric_points.clear()
        self.n_pharmacophoric_points = 0
        self.extractor = None
        self.molecular_system = None

    def to_ligandscout(self, file_name):
        """Method to export the pharmacophore to the ligandscout compatible format.

        Parameters
        ----------
        file_name : str
            Name of file to be written with the ligandscout format of the pharmacophore.

        Note
        ----
        Nothing is returned. A new file is written.

        """
        return to_ligandscout(self, file_name=file_name)

    def to_pharmer(self, file_name):
        """Method to export the pharmacophore to the pharmer compatible format.

        Parameters
        ----------
        file_name : str
            Name of file to be written with the pharmer format of the pharmacophore.

        Note
        ----
            Nothing is returned. A new file is written.

        """
        return to_pharmer(self, file_name=file_name)

    def to_pharmagist(self, file_name):
        """Method to export the pharmacophore to the pharmagist compatible format.

        Parameters
        ----------
        file_name : str
            Name of file to be written with the pharmagist format of the pharmacophore.

        Note
        ----
            Nothing is returned. A new file is written.

        """
        return to_pharmagist(self, file_name=file_name)
    
    def to_moe(self, file_name):
        """Method to export the pharmacophore to the MOE compatible format.

        Parameters
        ----------
        file_name: str
            Name of file to be written with the MOE format of the pharmacophore.

        Note
        ----
            Nothing is returned. A new file is written.

        """
        return to_moe(self, file_name=file_name)
    
    def to_rdkit(self):
        """ Returns an rdkit pharmacophore with the pharmacophoric_points from the original pharmacophore. 
            
            rdkit pharmacophores do not store the pharmacophoric_points radii, so they are returned as well.

            Returns
            -------
            rdkit_pharmacophore : rdkit.Chem.Pharm3D.Pharmacophore
                The rdkit pharmacophore.

            radii : list of float
                List with the radius in angstroms of each pharmacophoric point.
        """
        rdkit_element_name = { # dictionary to map openpharmacophore feature names to rdkit feature names
        "aromatic ring": "Aromatic",
        "hydrophobicity": "Hydrophobe",
        "hb acceptor": "Acceptor",
        "hb donor": "Donor",
        "positive charge": "PosIonizable",
        "negative charge": "NegIonizable",
        }

        points = []
        radii = []

        for element in self.pharmacophoric_points:
            feat_name = rdkit_element_name[element.feature_name]
            center = puw.get_value(element.center, to_unit="angstroms")
            center = Geometry.Point3D(center[0], center[1], center[2])
            points.append(ChemicalFeatures.FreeChemicalFeature(
                feat_name,
                center
            ))
            radius = puw.get_value(element.radius, to_unit="angstroms")
            radii.append(radius)

        rdkit_pharmacophore = rdkitPharmacophore.Pharmacophore(points)
        return rdkit_pharmacophore, radii
    
    def to_nx_graph(self, dmin=2.0, dmax=13.0, bin_size=1.0):
        """ Obtain a networkx graph representation of the pharmacophore.
        
            The pharmacophore graph is a graph whose nodes are pharmacophoric features and
            its edges are the euclidean distance between those features. The distance is 
            discretized into bins so more molecules can match the pharmacophore.
        
            Parameters
            ----------
            dmin : float
                The minimun distance in angstroms from which two pharmacophoric points are considered different.
            
            dmax : flaot
                The maximum distance in angstroms between pharmacohoric points.
                
            bin_size : float
                The size of the bins that will be used to bin the distances.
        
            Returns
            -------
            pharmacophore_graph : networkx.Graph
                The pharmacophore graph
        """
        pharmacophore_graph = nx.Graph()
        bins = np.arange(dmin, dmax, bin_size)
        # We keep track of feature counts to avoid repeated nodes
        feat_count = {
            "A" : 0,
            "D" : 0,
            "R" : 0,
            "H" : 0,
            "P" : 0,
            "N" : 0,
            "E" : 0,
            "I" : 0,
        }
        # First update the names with the count of each feature
        pharmacophoric_points = copy.deepcopy(self.pharmacophoric_points)
        for element in pharmacophoric_points:
            feat_count[element.short_name] += 1
            element.short_name += str(feat_count[element.short_name])            
        # Now we can add edges without repeating the nodes
        for points in itertools.combinations(pharmacophoric_points, 2):
            distance = distance_bewteen_pharmacophoric_points(points[0], points[1])
            binned_distance = discretize(distance, bins)
            pharmacophore_graph.add_edge(points[0].short_name,
                                         points[1].short_name,
                                         dis=binned_distance)
        
        return pharmacophore_graph
    
    def distance_matrix(self):
        """ Compute the distance matrix of the pharmacophore.
        
            Returns
            -------
            dis_matrix : np.ndarray of shape(n_pharmacophoric_points, n_pharmacophoric_points)
                The distance matrix.
        """
        n_pharmacophoric_points = self.n_pharmacophoric_points
        dis_matrix = np.zeros((n_pharmacophoric_points, n_pharmacophoric_points))
        
        for ii in range(n_pharmacophoric_points):
            for jj in range(ii, n_pharmacophoric_points):
                if ii == jj:
                    dis_matrix[ii, jj] = 0
                else:
                    distance = distance_bewteen_pharmacophoric_points(
                            self.pharmacophoric_points[ii],
                            self.pharmacophoric_points[jj])
                    dis_matrix[ii, jj] = distance
                    dis_matrix[jj, ii] = distance
        
        return dis_matrix
    
    def feature_count(self):
        """ Count the number of features ot the same kind in the pharmacophore.
        
            Returns
            -------
            counter : dict
                Dictionary with the count of each feature
        """
        counter = {
            "aromatic ring":   0,
            "hydrophobicity":  0,
            "hb acceptor":     0,
            "hb donor":        0,
            "positive charge": 0,
            "negative charge": 0,
        }

        for element in self.pharmacophoric_points:
            counter[element.feature_name] += 1
            
        return counter

    
    def __eq__(self, other):
        """ Check equality between pharmacophores.

            Assumes that pharmacophoric points are sorted equally in both pharmacophores.
        """
        if isinstance(other, type(self)):
            if self.n_pharmacophoric_points == other.n_pharmacophoric_points:
                for ii in range(self.n_pharmacophoric_points):
                    if not self.pharmacophoric_points[ii] == other.pharmacophoric_points[ii]:
                        return False
                return True
        return False
    
    def __repr__(self):
        return f"{self.__class__.__name__}(n_pharmacophoric_points: {self.n_pharmacophoric_points})"

    