**Instrukcja obsługi aplikacji POMOKA**

**Wstęp**

POMOKA to aplikacja służąca do analizy statystycznej danych medycznych oraz wizualizacji wyników w postaci wykresów krzywych przeżycia. Program pozwala na:

- Wczytywanie plików CSV i XLSX zawierających dane pacjentów.

- Przeprowadzanie analiz statystycznych, takich jak testy Kolmogorowa-Smirnowa, Mann-Whitneya U, czy analiza pól pod krzywymi (AUC).

- Tworzenie raportów w formacie PDF lub PNG.

- Edytowanie wykresów.

**Rozpoczęcie pracy**

- Uruchomienie aplikacji

- Po uruchomieniu aplikacji zobaczysz główne okno z przyciskami i opcjami do obsługi programu.

**Wczytanie danych**

- Kliknij przycisk Upload data.

- Wybierz plik z danymi (obsługiwane formaty: CSV, XLSX).

- Określ, w której linii znajdują się nagłówki kolumn (domyślnie w pierwszej linii).

Aplikacja wyświetli informację o liczbie wierszy i kolumn wczytanego pliku.

**Wybór preferencji i zakresów**

Ustawienia preferencji

- Po wczytaniu danych pojawi się lista kolumn wczytanego pliku.

- Zaznacz interesujące Cię kolumny w sekcji preferencji.

Ustawianie zakresów

- Kliknij przycisk Set Range.

- Dla każdej wybranej kolumny określ zakres danych (np. 1-10 dla wartości liczbowych lub SVG, MVG dla wartości tekstowych).

Jeśli wybierzesz kolumnę age lub sex, program automatycznie rozpozna ich specjalne właściwości.

**Analiza danych**

Wybór testów statystycznych

- W sekcji Tests zaznacz testy, które chcesz przeprowadzić. 

Dostępne opcje:

- Mann-Whitney U test

- AUC

- AUC Interpolated

- Kolmogorow-Smirnow

- Kolmogorow-Smirnow Interpolated

- Average Difference Interpolated

**Wykonanie analizy**

- Kliknij przycisk Execute, aby rozpocząć analizę.

Wyniki testów zostaną wyświetlone w polu wyników oraz zapisane w systemie aplikacji.

**Dodawanie kolejnych krzywych**

- Ustaw preferencje i zakresy dla nowej grupy danych

- Kliknij przycisk Add next curve, aby dodać kolejną krzywą do istniejącego wykresu.

**Generowanie wykresów**

Tworzenie wykresów

- Po wykonaniu analizy program automatycznie wygeneruje wykres krzywej przeżycia.

- Możesz dostosować jego wygląd, korzystając z funkcji edycji wykresu.

Edytowanie wykresu

- Kliknij przycisk Edit Chart, aby otworzyć narzędzie edycji wykresu.

Opcje edycji obejmują:

- Dodawanie i usuwanie tytułów osi.

- Ustawianie czcionki osi.

- Zmiana stylu wykresu (np. czarno-biały).

- Dostosowanie zakresów osi.

- Włączanie i wyłączanie legendy.

**Generowanie raportów**

Tworzenie raportu

- Kliknij przycisk Generate Report.

W oknie dialogowym ustaw:

- Nazwę raportu.

- Format wyjściowy (PDF lub PNG).

- Czy wykres ma być zapisany osobno.

Raport zostanie zapisany w katalogu plots.

**Zawartość raportu**

Wygenerowany raport zawiera:

- Tytuł raportu.

- Metadane, takie jak nazwa raportu i data wygenerowania.

- Wyniki testów statystycznych.

- Wykres krzywych przeżycia.

**Zakończenie pracy**

Zamykanie aplikacji:

- Kliknij przycisk Close the POMOKA app lub naciśnij klawisz ESC.

- Aplikacja zapyta o potwierdzenie przed zamknięciem.

Zerowanie ustawień

- Jeśli chcesz rozpocząć nową analizę bez zamykania aplikacji, kliknij przycisk Break w sekcji wykonania.

- Program wyczyści wszystkie bieżące ustawienia i wyniki.

**Uwagi końcowe**

- Upewnij się, że dane wejściowe są poprawnie sformatowane i zawierają wszystkie wymagane kolumny.

- Przed generowaniem raportu upewnij się, że wykres został wygenerowany i dane zostały przeanalizowane.

- **W razie problemów z działaniem aplikacji skontaktuj się z administratorem.**