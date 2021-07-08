from openpharmacophore.pharmacophoric_features import PositiveCharge
from openpharmacophore.pharmacophoric_shapes import Point, Sphere, GaussianKernel

class PositiveChargePoint(PositiveCharge, Point):

    def __init__(self, position):

        PositiveCharge.__init__(self)
        Point.__init__(self, position)

class PositiveChargeSphere(PositiveCharge, Sphere):

    def __init__(self, center, radius):

        PositiveCharge.__init__(self)
        Sphere.__init__(self, center, radius)

class PositiveChargeGaussianKernel(PositiveCharge, GaussianKernel):

    def __init__(self, center, sigma):

        PositiveCharge.__init__(self)
        GaussianKernel.__init__(self, center, sigma)
