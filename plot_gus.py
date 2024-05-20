import openpyxl
import os
from openpyxl import Workbook

def prepare_data(file_path):
    wiersze = 101  # Przetwarzamy tylko wiek od 0 do 100
    kolumny = 33
    tab_m = [[None] * kolumny for _ in range(wiersze)]
    tab_k = [[None] * kolumny for _ in range(wiersze)]

    # Otwórz plik Excel
    wb = openpyxl.load_workbook(file_path)

    # Zakładamy, że mamy 33 zakładki do przetworzenia
    liczba_zakladek = 33

    # Iteracja przez zakładki
    for i in range(1990, 1990 + liczba_zakladek):
        # Składanie nazwy zakładki
        nazwa_zakladki = f'{i}'

        # Wybór zakładki
        sheet = wb[nazwa_zakladki]

        # Przetwarzanie danych dla mężczyzn
        for j in range(5, 105):
            wiersz = j
            kolumna = 'D'
            wartosc = sheet[f'{kolumna}{wiersz}'].value
            if wartosc is not None:
                tab_m[j - 5][i - 1990] = 1 - wartosc

        # Przetwarzanie danych dla kobiet
        for j in range(106, 206):
            wiersz = j
            kolumna = 'D'
            wartosc = sheet[f'{kolumna}{wiersz}'].value
            if wartosc is not None:
                tab_k[j - 106][i - 1990] = 1 - wartosc

    return tab_m, tab_k

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
    for k in range(0, wiersze):
        dane = []
        i, j = k, 0
        while i < wiersze and j < kolumny:
            dane.append(macierz[i][j])
            i += 1
            j += 1
        dane_wykres.append(dane)

    return dane_wykres

def save_data_to_excel(file_path_men, file_path_women, tab_m, tab_k):
    # Zapisanie danych dla mężczyzn
    wb_m = Workbook()
    ws_m = wb_m.active
    ws_m.title = "Mężczyźni"

    # Dodaj nagłówki kolumn (punkty)
    years = list(range(0, 32))
    ws_m.append(["Punkt "] + years)

    # Dodaj wiersze z wiekiem (0-100)
    for age in range(134):
        ws_m.append([age])

    # Dodaj dane do arkusza "Mężczyźni"
    dane_do_wykresu_M = dane_wykresy(tab_m)
    for row_index, row_data in enumerate(dane_do_wykresu_M, start=2):
        probability = 1
        for col_index, value in enumerate(row_data, start=2):
            if value is not None:
                probability *= value
            ws_m.cell(row=row_index, column=col_index, value=probability * 100)

    wb_m.save(file_path_men)
    print(f"Dane zostały zapisane do pliku {file_path_men}")

    # Zapisanie danych dla kobiet
    wb_k = Workbook()
    ws_k = wb_k.active
    ws_k.title = "Kobiety"

    # Dodaj nagłówki kolumn (lata)
    ws_k.append(["Wiek"] + years)

    # Dodaj wiersze z wiekiem (0-100)
    for age in range(134):
        ws_k.append([age])

    # Dodaj dane do arkusza "Kobiety"
    dane_do_wykresu_K = dane_wykresy(tab_k)
    for row_index, row_data in enumerate(dane_do_wykresu_K, start=2):
        probability = 1
        for col_index, value in enumerate(row_data, start=2):
            if value is not None:
                probability *= value
            ws_k.cell(row=row_index, column=col_index, value=probability * 100)

    wb_k.save(file_path_women)
    print(f"Dane zostały zapisane do pliku {file_path_women}")

# Główna część programu
file_path = 'tablice_trwania_zycia_w_latach_1990-2022.xlsx'
file_path_men = 'dane_mezczyzni.xlsx'
file_path_women = 'dane_kobiety.xlsx'

# Przygotowanie danych
#tab_m, tab_k = prepare_data(file_path)

# Zapisanie danych do osobnych plików Excel
#save_data_to_excel(file_path_men, file_path_women, tab_m, tab_k)





#############################################################################################################



########## STARE #########
# wiersze = 121
# kolumny = 33
# tab_m = [[None]*kolumny for _ in range(wiersze)]
# tab_k = [[None]*kolumny for _ in range(wiersze)]
#
# # Otwórz plik Excel
# wb = openpyxl.load_workbook('tablice_trwania_zycia_w_latach_1990-2022.xlsx')
#
# # Zakładamy, że mamy 5 zakładek do przetworzenia
# liczba_zakladek = 33
#
# # Inicjalizacja listy dla przechowywania danych
# lista_danych = []
#
# # Iteracja przez zakładki
# for i in range(1990, 1990+liczba_zakladek):
#     # Składanie nazwy zakładki
#     nazwa_zakladki = f'{i}'
#
#     # Wybór zakładki
#     sheet = wb[nazwa_zakladki]
#     for j in range(5, 105):
#         wiersz = j
#         kolumna = 'D'
#         wartosc = sheet[f'{kolumna}{wiersz}'].value
#         if wartosc is not None:
#             tab_m[j-5][i-1990]=1-wartosc
#
#     for j in range(106, 206):
#         wiersz = j
#         kolumna = 'D'
#         wartosc = sheet[f'{kolumna}{wiersz}'].value
#         if wartosc is not None:
#             tab_k[j-106][i-1990]=1-wartosc
#     # Pobranie wartości z określonej komórki, np. B4
#    # wiersz = 4
#    # kolumna = 'B'
#    # wartosc = sheet[f'{kolumna}{wiersz}'].value
#
#     # Opcjonalnie: Sprawdź, czy wartość jest liczbą
#    # if isinstance(wartosc, (int, float)):
#         # Dodaj wartość do listy danych
#     #    lista_danych.append(wartosc)
#
# # Wyświetl zebrane dane
# print(tab_m)
# print(tab_k)
#
#
# def dane_wykresy(macierz):
#     wiersze = len(macierz)
#     kolumny = len(macierz[0])
#     dane_wykres = []
#
#     # Od prawego górnego rogu do lewego dolnego rogu
#     for k in range(kolumny - 1, -1, -1):
#         dane = []
#         i, j = 0, k
#         while j < kolumny and i < wiersze:
#             dane.append(macierz[i][j])
#             i += 1
#             j += 1
#         dane_wykres.append(dane)
#
#     # Od drugiego wiersza do ostatniego
#     for k in range(1, wiersze):
#         dane = []
#         i, j = k, 0
#         while i < wiersze and j < kolumny:
#             dane.append(macierz[i][j])
#             i += 1
#             j += 1
#         dane_wykres.append(dane)
#
#     return dane_wykres
#
# dane_do_wykresu_M = dane_wykresy(tab_m)
# dane_do_wykresu_K = dane_wykresy(tab_k)
#
# for i, dane in enumerate(dane_do_wykresu_M, 1):
#     plt.figure(figsize=(6, 4))
#     plt.plot(dane, marker='o', label=f'Seria {i}')
#     plt.title(f'Mezczyzna rocznik {2023-i}')
#     plt.xlabel('Rok')
#     plt.ylabel('Prawd. przeżycia')
#     plt.legend()
#     plt.savefig(f'C:/Users/gmozd/.PyCharmCE2019.2/config/scratches/POMOKA/Wykresy_mezczyzni/M_{2023-i}.png')
#     plt.close()
#
# for i, dane in enumerate(dane_do_wykresu_K, 1):
#     plt.figure(figsize=(6, 4))
#     plt.plot(dane, marker='o', label=f'Seria {i}')
#     plt.title(f'Kobieta rocznik {2023-i}')
#     plt.xlabel('Rok')
#     plt.ylabel('Prawd. przeżycia')
#     plt.legend()
#     plt.savefig(f'C:/Users/gmozd/.PyCharmCE2019.2/config/scratches/POMOKA/Wykresy_kobiety/K_{2023-i}.png')
#     plt.close()