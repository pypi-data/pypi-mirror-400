from .geometry_model import ScalarGeometry, VectorGeometry
from .kerr_geometry import KerrGeometry

class OrbitDynamics(object):
    def __init__(self,spin=0,Kerr=False):
        self._kerr = Kerr
        if spin==0 and not(Kerr):
            self._model = ScalarGeometry()
        elif spin==1 and not(Kerr):
            self._model = VectorGeometry()
        elif Kerr:
            self._model = KerrGeometry
        else:
            raise ValueError("Spin %d not supported" %spin)
    def model(self,abh=0):
        if not(self._kerr):
            return self._model
        if self._kerr:
            return self._model(abh)


