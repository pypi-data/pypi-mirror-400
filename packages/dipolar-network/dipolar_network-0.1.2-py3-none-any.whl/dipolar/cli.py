import argparse
import sys
import numpy as np
import json
import os
from .network import DipolarNetwork


def load_data(filepath):
    """Pomocnicza funkcja do wczytywania CSV z nagłówkiem lub bez."""
    try:
        # Próbujemy pominąć nagłówek
        data = np.loadtxt(filepath, delimiter=',', skiprows=1)
    except ValueError:
        # Jeśli się nie uda, próbujemy czytać od pierwszej linii
        try:
            data = np.loadtxt(filepath, delimiter=',')
        except Exception as e:
            print(f"Błąd wczytywania pliku CSV: {e}")
            sys.exit(1)

    if data.shape[1] < 3:
        print("Błąd: Plik CSV musi mieć co najmniej 3 kolumny (x1, x2, label)")
        sys.exit(1)

    return data[:, :2], data[:, 2]


def main():
    # Konfiguracja parsera argumentów
    parser = argparse.ArgumentParser(
        description="Trenuje sieć DipolarNetwork na danych z pliku CSV i zapisuje wynik do JSON."
    )

    # Argumenty pozycyjne (wymagane)
    parser.add_argument("input_csv", help="Ścieżka do pliku wejściowego CSV")
    parser.add_argument("output_json", help="Ścieżka do pliku wynikowego JSON")

    # Argumenty opcjonalne (z flagami)
    parser.add_argument("-l","--layers", type=int, default=3, help="Maksymalna liczba warstw (domyślnie: 3)")
    parser.add_argument("-n","--neurons", type=int, default=10, help="Liczba neuronów na warstwę (domyślnie: 10)")
    parser.add_argument("-t","--time", type=float, default=10.0, help="Limit czasu w sekundach na warstwę (domyślnie: 10.0)")
    parser.add_argument("-a","--accuracy", type=float, default=1.0, help="Docelowa dokładność 0.0-1.0 (domyślnie: 1.0)")

    args = parser.parse_args()

    # 1. Wczytanie danych
    if not os.path.exists(args.input_csv):
        print(f"Błąd: Plik '{args.input_csv}' nie istnieje.")
        sys.exit(1)

    print(f"-> Wczytywanie danych z: {args.input_csv}")
    X, y = load_data(args.input_csv)
    print(f"   Załadowano {len(X)} próbek.")

    # 2. Trening
    print(f"-> Rozpoczynam trening (Warstwy: {args.layers}, Neurony: {args.neurons}, Limit: {args.time}s)...")
    model = DipolarNetwork(
        max_layers=args.layers,
        neurons_per_layer=args.neurons
    )

    model.fit(X, y, time_limit=args.time, target_accuracy=args.accuracy)
    print("-> Trening zakończony.")

    # 3. Zapis wyników
    params = model.get_parameters()

    try:
        with open(args.output_json, 'w', encoding='utf-8') as f:
            json.dump(params, f, indent=4)
        print(f"-> Sukces! Wyniki zapisano w: {args.output_json}")
    except Exception as e:
        print(f"Błąd zapisu pliku JSON: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()