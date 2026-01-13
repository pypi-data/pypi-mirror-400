import numpy as np


class Dipole:
    """
    Reprezentacja dipola – pary punktów z różnych klas.
    Na jego podstawie tworzymy hiperpłaszczyznę: symetralną odcinka p1–p2.

    Parametry
    ---------
    p1 : np.ndarray
        Punkt klasy A.
    p2 : np.ndarray
        Punkt klasy B.
    """

    def __init__(self, p1: np.ndarray, p2: np.ndarray):
        self.p1 = np.asarray(p1)
        self.p2 = np.asarray(p2)

    def compute_hyperplane(self):

        w = self.p2 - self.p1
        m = 0.5 * (self.p1 + self.p2)
        b = -np.dot(w, m)
        return w, b
