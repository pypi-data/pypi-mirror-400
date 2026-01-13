"""
geometry.py
-----------
Funkcje pomocnicze z zakresu geometrii obliczeniowej wykorzystywane przez neurony
i warstwy dipolowe.
"""

import numpy as np


def midpoint(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Zwraca środek odcinka między punktami a i b.
    """
    return (a + b) / 2.0


def normal_vector(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Zwraca wektor prostopadły do odcinka AB (czyli kierunek hiperpłaszczyzny-dipola).
    Jest to po prostu różnica punktów b - a.

    Parametry
    ---------
    a, b : np.ndarray
        Wektory punktów w R^n

    Zwraca
    -------
    np.ndarray : wektor normalny (nieznormalizowany)
    """
    return b - a


def compute_hyperplane(a: np.ndarray, b: np.ndarray):
    """
    Oblicza parametry hiperpłaszczyzny dipola.

    Hiperpłaszczyzna jest symetralną odcinka łączącego punkty:

        p1 = a
        p2 = b

    Wzory:
        w = p2 - p1
        m = (p1 + p2) / 2         (środek odcinka)
        b = - w · m               (tak aby w*m + b = 0)

    Zwraca:
        w, b

    Parametry
    ---------
    a, b : np.ndarray
        punkty tworzące dipol

    """
    w = normal_vector(a, b)
    m = midpoint(a, b)
    bias = -np.dot(w, m)
    return w, bias


def nearest_enemy_dipoles(X, y, k):
    """
    Znajduje k par najbliższych punktów z przeciwnych klas.
    Zwraca listę krotek (p1, p2), gdzie wymuszona jest kolejność:
      - p1: punkt z klasy -1 (Czerwony)
      - p2: punkt z klasy  1 (Niebieski)
    """
    dipoles = []
    remaining_idx = list(range(len(X)))

    for _ in range(k):
        if len(remaining_idx) < 2:
            break

        best_pair = None
        best_dist = np.inf

        # 1. Szukamy pary najbliższych wrogów
        for i in remaining_idx:
            for j in remaining_idx:
                if i >= j:
                    continue
                if y[i] == y[j]:  # Muszą być z różnych klas
                    continue

                dist = np.linalg.norm(X[i] - X[j])
                if dist < best_dist:
                    best_dist = dist
                    best_pair = (i, j)

        if best_pair is None:
            break

        # 2. SORTOWANIE BIEGUNOWOŚCI
        # Wymuszamy, aby p1 należał do klasy -1, a p2 do klasy 1.
        idx_a, idx_b = best_pair

        if y[idx_a] == -1:
            # Kolejność jest poprawna: a=-1, b=1
            p1 = X[idx_a]
            p2 = X[idx_b]
        else:
            # Kolejność odwrotna: a=1, b=-1 (więc zamieniamy)
            p1 = X[idx_b]
            p2 = X[idx_a]

        dipoles.append((p1, p2))

        # 3. Sprzątanie indeksów
        remaining_idx.remove(idx_a)
        remaining_idx.remove(idx_b)

    return dipoles
