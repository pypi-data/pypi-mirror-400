"""
validation.py
--------------
Zestaw funkcji walidujących dane wejściowe i formaty zgodne z API.
"""

import numpy as np


def check_xy(X, y):
    """
    Sprawdza zgodność wymiarów X i y oraz konwertuje na tablice numpy.

    Parametry
    ---------
    X : array-like, shape (n_samples, n_features)
    y : array-like, shape (n_samples,)

    Zwraca
    -------
    X, y : numpy.ndarray
    """
    X = np.asarray(X)
    y = np.asarray(y)

    if len(X.shape) != 2:
        raise ValueError("X must be a 2D array (n_samples, n_features).")

    if y.shape[0] != X.shape[0]:
        raise ValueError("X and y must have the same number of samples.")

    return X, y


def check_class_labels(y):
    """
    Sprawdza, czy etykiety klas są binarne (0/1 lub -1/1).

    Jeśli są inne, użytkownik powinien wykonać mapowanie na 0/1.

    Zwraca:
        unique_labels : zbiór klas
    """
    unique = np.unique(y)
    if len(unique) > 2:
        raise ValueError(
            f"DipolarNetwork wspiera tylko klasyfikację binarną, "
            f"otrzymano klasy: {unique}"
        )
    return unique
