import numpy as np
from .neuron import Neuron


class Layer:
    """
    Warstwa neuronów dipolowych.
    Punkt jest klasyfikowany jako pozytywny *tylko jeśli* wszystkie neurony
    uznają go za poprawny (logiczna koniunkcja – AND).

    W praktyce oznacza to wycinanie wypukłego regionu.
    """

    def __init__(self):
        self.neurons: list[Neuron] = []

    def add_neuron(self, neuron: Neuron):
        """Dodaje neuron do warstwy."""
        self.neurons.append(neuron)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Koniunkcja predykcji neuronów.
        Każdy neuron zwraca {-1, 1}.

        Zwraca
        ------
        np.ndarray
            1 jeśli X spełnia wszystkie nierówności, inaczej 0.
        """
        if not self.neurons:
            return np.zeros(len(X), dtype=int)

        predictions = np.array([n.predict(X) for n in self.neurons])
        valid = np.all(predictions == 1, axis=0)
        return valid.astype(int)

    def __len__(self):
        return len(self.neurons)
