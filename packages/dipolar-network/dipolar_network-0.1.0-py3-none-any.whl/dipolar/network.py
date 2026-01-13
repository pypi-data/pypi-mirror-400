import numpy as np
import copy
import time
from itertools import combinations

from .layer import Layer
from .neuron import Neuron
from .dipole import Dipole

# Upewnij się, że masz tę funkcję dostępną (np. z importu)
from dipolar.utils.geometry import nearest_enemy_dipoles


class DipolarNetwork:
    # core/network.py

    def __init__(self, max_layers=3, neurons_per_layer=10):
        self.max_layers = max_layers
        self.neurons_per_layer = neurons_per_layer
        self.layers = []
        self.training_history = []
        # --- NOWE POLA ---
        self.train_time_total = 0.0
        self.train_time_best = 0.0
        self.best_global_step = 0
        # Zmieniamy definicję metody fit

    def fit(self, X: np.ndarray, y: np.ndarray, time_limit=None, target_accuracy=1.0):
        start_time = time.time()
        self.train_time_best = 0.0
        self.best_global_step = 0

        X = np.asarray(X)
        y = np.asarray(y)

        # Reset
        self.layers = []
        self.training_history = []

        global_best_acc = -1.0
        global_step_counter = 0

        # 1. Pobieramy dipole
        raw_dipoles = nearest_enemy_dipoles(X, y, self.neurons_per_layer)
        base_dipoles = sorted(raw_dipoles, key=lambda d: np.linalg.norm(d[0] - d[1]))

        for layer_idx in range(self.max_layers):
            if time_limit is not None and (time.time() - start_time > time_limit):
                print(f"Time limit reached before Layer {layer_idx + 1}. Stopping.")
                break

            # layer_idx = 0 -> kombinacje 1-elementowe
            # layer_idx = 1 -> kombinacje 2-elementowe (nawet jak poprzednią pominęliśmy)
            num_to_combine = layer_idx + 1

            subset_dipoles = base_dipoles[:self.neurons_per_layer]
            all_combinations = list(combinations(range(len(subset_dipoles)), num_to_combine))

            best_acc_in_layer = -1.0
            best_layer_obj = None
            best_step_in_layer = 0

            print(
                f"--- Layer {layer_idx + 1} (Size {num_to_combine}): Testing {len(all_combinations)} combinations ---")

            # Dodajemy tymczasowo pustą warstwę na koniec listy,
            # żeby mechanizm self.layers[-1] = ... działał poprawnie
            self.layers.append(Layer())
            current_list_index = len(self.layers) - 1

            for comb_idx, combo in enumerate(all_combinations):
                if time_limit is not None and (time.time() - start_time > time_limit):
                    print("Time limit reached inside loop. Stopping.")
                    break

                global_step_counter += 1

                layer = Layer()
                for dipole_idx in combo:
                    p1, p2 = subset_dipoles[dipole_idx]
                    d = Dipole(p1, p2)
                    w, b = d.compute_hyperplane()
                    neuron = Neuron()
                    neuron.weight = w;
                    neuron.bias = b;
                    neuron.p1 = p1;
                    neuron.p2 = p2
                    layer.add_neuron(neuron)

                # Podmieniamy ostatnią warstwę (tę, którą właśnie testujemy)
                self.layers[current_list_index] = layer

                preds = self.predict(X)
                acc = np.mean(preds == y)

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

                if acc > best_acc_in_layer:
                    self.train_time_best = time.time() - start_time
                    best_acc_in_layer = acc
                    best_layer_obj = copy.deepcopy(layer)
                    best_step_in_layer = global_step_counter

                if acc >= target_accuracy:
                    print(f"Target accuracy ({target_accuracy}) reached! Combo: {combo}")
                    self.train_time_best = time.time() - start_time
                    self.train_time_total = time.time() - start_time
                    self.best_global_step = global_step_counter
                    return self

            # === DECYZJA PO ZBADANIU WARSTWY ===

            if best_layer_obj and best_acc_in_layer > global_best_acc:
                # 1. SUKCES: Warstwa poprawiła wynik globalny
                self.layers[current_list_index] = best_layer_obj
                global_best_acc = best_acc_in_layer
                self.best_global_step = best_step_in_layer
                # self.train_time_best = time.time() - start_time
                print(f"Layer {layer_idx + 1} ACCEPTED. New Best: {global_best_acc:.4f}")
            else:
                # 2. PORAŻKA: Warstwa nie poprawiła wyniku
                # Zamiast break, robimy pop() i continue (idziemy głębiej)
                print(
                    f"Layer {layer_idx + 1} REJECTED (Acc: {best_acc_in_layer:.4f} <= Global: {global_best_acc:.4f}). Skipping to next layer...")

                self.layers.pop()  # Usuwamy tę nieudaną warstwę z listy
                # Pętla for idzie dalej -> layer_idx wzrośnie -> num_to_combine wzrośnie

        self.train_time_total = time.time() - start_time
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        result = np.zeros(len(X), dtype=int)
        for layer in self.layers:
            layer_pred = layer.predict(X)
            result = np.maximum(result, layer_pred)
        return np.where(result == 1, 1, -1)

    def get_parameters(self):
        """
        Zwraca strukturę parametrów modelu (hiperpłaszczyzny).
        Format: Lista warstw, gdzie każda warstwa to lista neuronów (słowników).
        """
        model_structure = []

        for i, layer in enumerate(self.layers):
            layer_data = []
            for neuron in layer.neurons:
                # Pobieramy wagi [w_x, w_y] i bias
                # Konwertujemy numpy na zwykłe listy/floaty dla łatwiejszego użycia
                w = neuron.weight.tolist() if hasattr(neuron.weight, 'tolist') else neuron.weight
                b = float(neuron.bias)

                # Równanie prostej: w[0]*x + w[1]*y + b = 0
                neuron_params = {
                    "weights": w,  # np. [0.5, -1.2]
                    "bias": b,  # np. 2.4
                    "equation": f"{w[0]:.3f}x + {w[1]:.3f}y + {b:.3f} = 0"  # Czytelny wzór
                }
                layer_data.append(neuron_params)

            model_structure.append(layer_data)

        return model_structure