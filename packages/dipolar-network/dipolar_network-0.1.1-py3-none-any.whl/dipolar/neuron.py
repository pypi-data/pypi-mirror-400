import numpy as np


class Neuron:
    """
    Pojedynczy neuron formalny reprezentujący hiperpłaszczyznę:
        w · x + b = 0

    Jest tworzony na podstawie dipola (p1, p2).
    """

    def __init__(self):
        # Punkty źródłowe (do wizualizacji)
        self.p1 = None
        self.p2 = None

        # Parametry hiperpłaszczyzny
        self.weight = None
        self.bias = None

        # --- NOWE ---
        # Wysokość neuronu w osi Z (do wizualizacji 3D)
        # domyślnie 0 przed trenowaniem
        self.z = 0.0

    # -------------------------------------------------------------------------
    # Alias zgodny z tym, czego oczekują pliki wizualizacji:
    # neuron.w  → weight
    # neuron.b  → bias
    # neuron.z  → wysokość dla 3D (NOWE)
    # -------------------------------------------------------------------------
    @property
    def w(self):
        return self.weight

    @property
    def b(self):
        return self.bias

    # -------------------------------------------------------------------------

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """
        Zwraca wartości funkcji liniowej: f(x) = w·x + b
        """
        if self.weight is None or self.bias is None:
            raise ValueError("Neuron is not initialized (weight/bias not set).")

        return np.dot(X, self.weight) + self.bias

    # -------------------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Zwraca 1 gdy f(x) >= 0, inaczej 0.
        """
        vals = self.decision_function(X)
        return (vals >= 0).astype(int)

    # -------------------------------------------------------------------------

    def contains(self, X: np.ndarray) -> np.ndarray:
        """
        Zwraca True jeśli punkt znajduje się w półprzestrzeni neuronu.
        """
        return self.predict(X).astype(bool)
