import argparse
import sys
import numpy as np
import json
import os
from .network import DipolarNetwork


def load_data(filepath):
    """
    Wczytuje CSV, gdzie pierwszy wiersz to nagłówek (opcjonalnie),
    kolumny od 0 do przedostatniej to cechy (X), a ostatnia to klasa (y).
    """
    data = None
    try:
        # KROK 1: Zakładamy, że jest nagłówek, więc pomijamy 1 wiersz (skiprows=1)
        data = np.loadtxt(filepath, delimiter=',', skiprows=1)
    except ValueError:
        # KROK 2: Jeśli się nie uda (np. brak nagłówka i same liczby), próbujemy czytać od początku
        try:
            data = np.loadtxt(filepath, delimiter=',')
        except Exception as e:
            print(f"Błąd wczytywania pliku CSV: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"Nieoczekiwany błąd przy otwieraniu pliku: {e}")
        sys.exit(1)

    # Sprawdzenie minimalnej liczby kolumn (min. 1 cecha + 1 etykieta = 2 kolumny)
    if data.ndim == 1:
        # Zabezpieczenie na wypadek, gdyby np.loadtxt spłaszczył wektor
        print("Błąd: Plik CSV wydaje się mieć tylko jedną kolumnę lub jest pusty.")
        sys.exit(1)

    if data.shape[1] < 2:
        print("Błąd: Plik CSV musi mieć co najmniej 2 kolumny (cecha, label).")
        sys.exit(1)

    # --- KLUCZOWA ZMIANA DLA N-WYMIARÓW ---
    # X: Wszystkie wiersze, wszystkie kolumny OPRÓCZ ostatniej ([:-1])
    # y: Wszystkie wiersze, TYLKO ostatnia kolumna ([-1])
    X = data[:, :-1]
    y = data[:, -1]

    return X, y


def main():
    # Konfiguracja parsera argumentów
    parser = argparse.ArgumentParser(
        description="Trenuje sieć DipolarNetwork na danych N-wymiarowych z pliku CSV."
    )

    # Argumenty pozycyjne (wymagane)
    parser.add_argument("input_csv", help="Ścieżka do pliku wejściowego CSV (ostatnia kolumna to klasa)")
    parser.add_argument("output_json", help="Ścieżka do pliku wynikowego JSON")

    # Argumenty opcjonalne (z flagami)
    parser.add_argument("-l", "--layers", type=int, default=3, help="Maksymalna liczba warstw (domyślnie: 3)")
    parser.add_argument("-n", "--neurons", type=int, default=10, help="Liczba neuronów na warstwę (domyślnie: 10)")
    parser.add_argument("-t", "--time", type=float, default=10.0,
                        help="Limit czasu w sekundach na warstwę (domyślnie: 10.0)")
    parser.add_argument("-a", "--accuracy", type=float, default=1.0,
                        help="Docelowa dokładność 0.0-1.0 (domyślnie: 1.0)")

    args = parser.parse_args()

    # 1. Weryfikacja pliku
    if not os.path.exists(args.input_csv):
        print(f"Błąd: Plik '{args.input_csv}' nie istnieje.")
        sys.exit(1)

    print(f"-> Wczytywanie danych z: {args.input_csv}")

    # Wczytanie danych
    X, y = load_data(args.input_csv)

    # Informacja zwrotna o wymiarowości
    n_samples, n_features = X.shape
    print(f"   Załadowano {n_samples} próbek.")
    print(f"   Wykryto {n_features} wymiarów (cech).")

    # 2. Trening
    print(f"-> Rozpoczynam trening (Warstwy: {args.layers}, Neurony: {args.neurons}, Limit: {args.time}s)...")

    try:
        model = DipolarNetwork(
            max_layers=args.layers,
            neurons_per_layer=args.neurons
        )

        model.fit(X, y, time_limit=args.time, target_accuracy=args.accuracy)
        stats = model.get_statistics()
        acc_str = stats.get("accuracy_percent", "N/A")
        time_str = stats.get("execution_time_sec", 0)
        print(f"\n-> Trening zakończony. Skuteczność: {acc_str} (Czas: {time_str}s)")

    except Exception as e:
        print(f"Błąd krytyczny podczas treningu: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 3. Zapis wyników
    try:
        params = model.get_parameters()
        with open(args.output_json, 'w', encoding='utf-8') as f:
            json.dump(params, f, indent=4)
        print(f"-> Sukces! Wyniki zapisano w: {args.output_json}")
    except Exception as e:
        print(f"Błąd zapisu pliku JSON: {e}")
        sys.exit(1)

    print()


if __name__ == "__main__":
    main()