import numpy as np
import copy
import time
from itertools import combinations

from .layer import Layer
from .neuron import Neuron
from .dipole import Dipole

# Zakładam, że ta ścieżka jest poprawna w Twoim projekcie
from dipolar.utils.geometry import nearest_enemy_dipoles


class DipolarNetwork:

    def __init__(self, max_layers=3, neurons_per_layer=10):
        self.max_layers = max_layers
        self.neurons_per_layer = neurons_per_layer
        self.layers = []
        self.training_history = []

        # Statystyki treningu
        self.train_time_total = 0.0
        self.train_time_best = 0.0
        self.best_global_step = 0

        self.n_samples = 0  # Łączna liczba próbek
        self.n_pos = 0  # Liczba próbek klasy 1
        self.n_neg = 0
        # Nowe pola do raportowania
        self.execution_time = 0.0
        self.final_accuracy = 0.0
        self.input_dim = 0
        self.is_fitted = False

    def score(self, X, y):
        """
        Zwraca dokładność (accuracy) modelu na podanych danych.
        """
        if not self.layers:
            return 0.0

        preds = self.predict(X)
        # Porównujemy predykcje z etykietami.
        # Uwaga: predict zwraca -1/1. Upewnij się, że y też jest w tym formacie.
        correct = np.sum(preds.astype(int) == y.astype(int))
        return correct / len(y)

    def fit(self, X: np.ndarray, y: np.ndarray, time_limit=None, target_accuracy=1.0):
        start_time = time.time()

        # Resetujemy stan
        self.train_time_best = 0.0
        self.best_global_step = 0
        self.is_fitted = False

        X = np.asarray(X)
        y = np.asarray(y)

        # Zapisujemy wymiar danych (dla raportu)
        self.input_dim = X.shape[1] if len(X.shape) > 1 else 1
        self.n_samples = int(len(y))
        self.n_pos = int(np.sum(y == 1))
        self.n_neg = int(self.n_samples - self.n_pos)
        self.layers = []
        self.training_history = []

        global_best_acc = -1.0
        global_step_counter = 0

        # 1. Pobieramy dipole
        raw_dipoles = nearest_enemy_dipoles(X, y, self.neurons_per_layer)
        base_dipoles = sorted(raw_dipoles, key=lambda d: np.linalg.norm(d[0] - d[1]))

        # --- GŁÓWNA PĘTLA PO WARSTWACH ---
        for layer_idx in range(self.max_layers):
            if time_limit is not None and (time.time() - start_time > time_limit):
                print(f"Time limit reached before Layer {layer_idx + 1}. Stopping.")
                break

            num_to_combine = layer_idx + 1
            subset_dipoles = base_dipoles[:self.neurons_per_layer]
            all_combinations = list(combinations(range(len(subset_dipoles)), num_to_combine))

            best_acc_in_layer = -1.0
            best_layer_obj = None
            best_step_in_layer = 0

            # print(
            #     f"--- Layer {layer_idx + 1} (Size {num_to_combine}): Testing {len(all_combinations)} combinations ---")

            self.layers.append(Layer())
            current_list_index = len(self.layers) - 1

            for comb_idx, combo in enumerate(all_combinations):
                if time_limit is not None and (time.time() - start_time > time_limit):
                    print("Time limit reached inside loop. Stopping.")
                    break

                global_step_counter += 1

                # Budowanie warstwy z dipoli
                layer = Layer()
                for dipole_idx in combo:
                    p1, p2 = subset_dipoles[dipole_idx]
                    d = Dipole(p1, p2)
                    w, b = d.compute_hyperplane()

                    neuron = Neuron()
                    neuron.weight = w
                    neuron.bias = b
                    neuron.p1 = p1
                    neuron.p2 = p2
                    layer.add_neuron(neuron)

                # Podmieniamy ostatnią warstwę
                self.layers[current_list_index] = layer

                # Sprawdzamy wynik
                preds = self.predict(X)
                acc = np.mean(preds == y)

                # Historia treningu (dla GUI)
                step_data = {
                    'layers': copy.deepcopy(self.layers),
                    'accuracy': acc,
                    'combo': combo,
                    'layer_idx': layer_idx,
                    'candidates': subset_dipoles,
                    'combo_current': comb_idx + 1,
                    'combo_total': len(all_combinations),
                    'global_step': global_step_counter
                }
                self.training_history.append(step_data)

                # Logika "Best in Layer"
                if acc > best_acc_in_layer:
                    self.train_time_best = time.time() - start_time
                    best_acc_in_layer = acc
                    best_layer_obj = copy.deepcopy(layer)
                    best_step_in_layer = global_step_counter

                # --- SUKCES (Target osiągnięty) ---
                if acc >= target_accuracy:
                    print(f"Target accuracy ({target_accuracy}) reached! Combo: {combo}")

                    # Zapisujemy statystyki końcowe
                    self.train_time_total = time.time() - start_time
                    self.best_global_step = global_step_counter

                    # Standardowe pola statystyk (dla CLI/GUI)
                    self.execution_time = self.train_time_total
                    self.final_accuracy = acc
                    self.is_fitted = True

                    return self

            # === DECYZJA PO ZBADANIU CAŁEJ WARSTWY ===
            if best_layer_obj and best_acc_in_layer > global_best_acc:
                # Akceptujemy warstwę
                self.layers[current_list_index] = best_layer_obj
                global_best_acc = best_acc_in_layer
                self.best_global_step = best_step_in_layer
                print(f"Layer {layer_idx + 1} ACCEPTED. New Best: {global_best_acc:.4f}")
            else:
                # Odrzucamy warstwę (backtracking/skip)
                print(
                    f"Layer {layer_idx + 1} REJECTED (Acc: {best_acc_in_layer:.4f} <= Global: {global_best_acc:.4f}). Skipping...")
                self.layers.pop()

        # --- KONIEC TRENINGU (Bez osiągnięcia celu lub limit czasu) ---
        self.train_time_total = time.time() - start_time

        # Zapisujemy statystyki końcowe
        self.execution_time = self.train_time_total
        self.is_fitted = True

        # Obliczamy finalne accuracy (na wypadek gdyby fit nie zwrócił wcześniej)
        self.final_accuracy = self.score(X, y)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        if len(self.layers) == 0:
            # Jeśli brak warstw, zwracamy same zera (lub losowe)
            return np.zeros(len(X), dtype=int)

        result = np.zeros(len(X), dtype=int)

        # Dipolar logic: result is OR (maximum) of layers
        for layer in self.layers:
            layer_pred = layer.predict(X)
            # Zakładamy, że layer.predict zwraca 0/1 lub -1/1.
            # W logice dipolowej często szukamy "przynajmniej jednego 1".
            result = np.maximum(result, layer_pred)

        # Normalizacja do formatu -1 / 1
        return np.where(result == 1, 1, -1)

    def _format_equation(self, weights, bias):
        """
        Metoda pomocnicza do formatowania równania (obsługuje N-wymiarów).
        """
        n_dims = len(weights)
        parts = []

        for i, w in enumerate(weights):
            if n_dims == 2:
                var_name = "x" if i == 0 else "y"
            elif n_dims == 3:
                var_names = ["x", "y", "z"]
                var_name = var_names[i]
            else:
                var_name = f"x{i + 1}"

            val_str = f"{abs(w):.3f}*{var_name}"

            if i == 0:
                prefix = "-" if w < 0 else ""
                parts.append(f"{prefix}{val_str}")
            else:
                operator = " + " if w >= 0 else " - "
                parts.append(f"{operator}{val_str}")

        operator = " + " if bias >= 0 else " - "
        parts.append(f"{operator}{abs(bias):.3f}")

        return "".join(parts) + " = 0"

    def get_statistics(self):
        """
        Zwraca słownik ze statystykami.
        Wspólne źródło danych dla GUI i CLI.
        """
        total_neurons = sum(len(layer.neurons) for layer in self.layers)

        return {
            "execution_time_sec": round(self.execution_time, 4),
            "accuracy": round(self.final_accuracy, 4),
            "accuracy_percent": f"{self.final_accuracy * 100:.2f}%",
            "dataset_info": {
                "total_samples": self.n_samples,
                "positive_class": self.n_pos,  # Np. klasa 1
                "negative_class": self.n_neg,  # Np. klasa -1 lub 0
                "input_dimensions": self.input_dim
            },
            "model_info": {
                "total_layers": len(self.layers),
                "total_neurons": total_neurons,
                "best_global_step": self.best_global_step
            },
            "parameters_config": {
                "max_layers": self.max_layers,
                "neurons_per_layer": self.neurons_per_layer
            }
        }

    def get_parameters(self):
        """
        Zwraca pełny zrzut modelu do zapisu w JSON (struktura + statystyki).
        """
        layers_data = []

        for i, layer in enumerate(self.layers):
            layer_data = []
            for neuron in layer.neurons:
                # Pobieranie wag w bezpieczny sposób
                if hasattr(neuron, 'weight') and hasattr(neuron.weight, 'tolist'):
                    w = neuron.weight.tolist()
                elif hasattr(neuron, 'weights') and hasattr(neuron.weights, 'tolist'):
                    w = neuron.weights.tolist()
                else:
                    w = getattr(neuron, 'weight', getattr(neuron, 'weights', []))

                b = float(neuron.bias)
                eq_string = self._format_equation(w, b)

                neuron_params = {
                    "weights": w,
                    "bias": b,
                    "equation": eq_string
                }
                layer_data.append(neuron_params)

            layers_data.append(layer_data)

        # Pobieramy statystyki z nowej funkcji
        stats = self.get_statistics()

        return {
            "statistics": stats,
            "model_structure": layers_data
        }