import pyunitwizard as puw
from openpharmacophore import pharmacophoric_elements

def rdkit_to_point(feat_name, coords, radius=None, direction=None, sigma=None, point_type="spheres"):

    """Transform an rdkit feature point to an openpharmacophore pharmacophoric element"""

    points = {
        "spheres": {
            "Acceptor": pharmacophoric_elements.HBAcceptorSphere,
            "Donor": pharmacophoric_elements.HBDonorSphere,
            "Aromatic": pharmacophoric_elements.AromaticRingSphere,
            "Hydrophobe": pharmacophoric_elements.HydrophobicSphere,
            "PosIonizable": pharmacophoric_elements.PositiveChargeSphere,
            "NegIonizable": pharmacophoric_elements.NegativeChargeSphere,
        },
        "spheres_vectors": {
            "Acceptor": pharmacophoric_elements.HBAcceptorSphereAndVector,
            "Donor": pharmacophoric_elements.HBDonorSphereAndVector,
            "Aromatic": pharmacophoric_elements.AromaticRingSphereAndVector,
            "Hydrophobe": pharmacophoric_elements.HydrophobicSphere,
            "PosIonizable": pharmacophoric_elements.PositiveChargeSphere,
            "NegIonizable": pharmacophoric_elements.NegativeChargeSphere,
        },
        "gaussian": {
            "Acceptor": pharmacophoric_elements.HBAcceptorGaussianKernel,
            "Donor": pharmacophoric_elements.HBAcceptorGaussianKernel,
            "Aromatic": pharmacophoric_elements.aromatic_ring.AromaticRingGaussianKernel,
            "Hydrophobe": pharmacophoric_elements.HydrophobicGaussianKernel,
            "PosIonizable": pharmacophoric_elements.PositiveChargeGaussianKernel,
            "NegIonizable": pharmacophoric_elements.NegativeChargeGaussianKernel,
        },
        "shapelet": {
            "Acceptor": pharmacophoric_elements.HBAcceptorSphere,
            "Donor": pharmacophoric_elements.HBDonorSphere,
            "Aromatic": pharmacophoric_elements.AromaticRingShapelet,
            "Hydrophobe": pharmacophoric_elements.HydrophobicShapelet,
            "PosIonizable": pharmacophoric_elements.PositiveChargeSphere,
            "NegIonizable": pharmacophoric_elements.NegativeChargeSphere,
        },
    }

    if point_type == "spheres":
        point = points["spheres"][feat_name](center=puw.quantity(coords, "angstroms"), 
                                            radius=puw.quantity(radius, "angstroms"))
    elif point_type == "spheres_vectors":
        point = points["spheres_vectors"][feat_name](center=puw.quantity(coords, "angstroms"), 
                                            radius=puw.quantity(radius, "angstroms"),
                                            direction=direction)
    elif point_type == "gaussian":
        point = points["gaussian"][feat_name](center=puw.quantity(coords, "angstroms"),
                                            sigma=puw.quantity(sigma, "angstroms"))
    else:
        raise NotImplementedError
    
    # TODO: incorporate other point types. Shapelet is missing phamracophoric element types.

    return point