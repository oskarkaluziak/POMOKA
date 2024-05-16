import openpyxl
import matplotlib.pyplot as plt

wiersze = 121
kolumny = 33
tab_m = [[None]*kolumny for _ in range(wiersze)]
tab_k = [[None]*kolumny for _ in range(wiersze)]

# Otwórz plik Excel
wb = openpyxl.load_workbook('tablice_trwania_zycia_w_latach_1990-2022.xlsx')

# Zakładamy, że mamy 5 zakładek do przetworzenia
liczba_zakladek = 33

# Inicjalizacja listy dla przechowywania danych
lista_danych = []

# Iteracja przez zakładki
for i in range(1990, 1990+liczba_zakladek):
    # Składanie nazwy zakładki
    nazwa_zakladki = f'{i}'

    # Wybór zakładki
    sheet = wb[nazwa_zakladki]
    for j in range(5, 105):
        wiersz = j
        kolumna = 'D'
        wartosc = sheet[f'{kolumna}{wiersz}'].value
        if wartosc is not None:
            tab_m[j-5][i-1990]=1-wartosc

    for j in range(106, 206):
        wiersz = j
        kolumna = 'D'
        wartosc = sheet[f'{kolumna}{wiersz}'].value
        if wartosc is not None:
            tab_k[j-106][i-1990]=1-wartosc
    # Pobranie wartości z określonej komórki, np. B4
   # wiersz = 4
   # kolumna = 'B'
   # wartosc = sheet[f'{kolumna}{wiersz}'].value

    # Opcjonalnie: Sprawdź, czy wartość jest liczbą
   # if isinstance(wartosc, (int, float)):
        # Dodaj wartość do listy danych
    #    lista_danych.append(wartosc)

# Wyświetl zebrane dane
print(tab_m)
print(tab_k)


def dane_wykresy(macierz):
    wiersze = len(macierz)
    kolumny = len(macierz[0])
    dane_wykres = []

    # Od prawego górnego rogu do lewego dolnego rogu
    for k in range(kolumny - 1, -1, -1):
        dane = []
        i, j = 0, k
        while j < kolumny and i < wiersze:
            dane.append(macierz[i][j])
            i += 1
            j += 1
        dane_wykres.append(dane)

    # Od drugiego wiersza do ostatniego
    for k in range(1, wiersze):
        dane = []
        i, j = k, 0
        while i < wiersze and j < kolumny:
            dane.append(macierz[i][j])
            i += 1
            j += 1
        dane_wykres.append(dane)

    return dane_wykres

dane_do_wykresu_M = dane_wykresy(tab_m)
dane_do_wykresu_K = dane_wykresy(tab_k)

for i, dane in enumerate(dane_do_wykresu_M, 1):
    plt.figure(figsize=(6, 4))
    plt.plot(dane, marker='o', label=f'Seria {i}')
    plt.title(f'Mezczyzna rocznik {2023-i}')
    plt.xlabel('Rok')
    plt.ylabel('Prawd. przeżycia')
    plt.legend()
    plt.savefig(f'C:/Users/gmozd/.PyCharmCE2019.2/config/scratches/POMOKA/Wykresy_mezczyzni/M_{2023-i}.png')
    plt.close()

for i, dane in enumerate(dane_do_wykresu_K, 1):
    plt.figure(figsize=(6, 4))
    plt.plot(dane, marker='o', label=f'Seria {i}')
    plt.title(f'Kobieta rocznik {2023-i}')
    plt.xlabel('Rok')
    plt.ylabel('Prawd. przeżycia')
    plt.legend()
    plt.savefig(f'C:/Users/gmozd/.PyCharmCE2019.2/config/scratches/POMOKA/Wykresy_kobiety/K_{2023-i}.png')
    plt.close()