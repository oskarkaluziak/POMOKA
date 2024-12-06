import os
import sys
from datetime import datetime

# PyQt5 imports
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout,
    QVBoxLayout, QFileDialog, QAbstractItemView, QListWidget, QInputDialog)
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5.QtCore import Qt

# Data handling and analysis
import pandas as pd
import numpy as np

# Matplotlib for plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Lifelines for survival analysis
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test #(delete when new tests come in)

# Custom imports
from plot_gus import prepare_data, save_data_to_excel, lineChartOne, lineChartRange

class POMOKAstat(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.interface()
        self.isExecuting = False
        self.column_ranges = {}
        self.curves_data = []

    def interface(self):  # interface apki
        self.label1 = QLabel("<b>Be sure to read the detailed instructions for using the program!<b>", self)
        self.label2 = QLabel("<b>Results:<b>", self)

        self.filePathEdt = QLineEdit()
        self.resultEdt = QLineEdit()
        self.resultEdt.setReadOnly(True)

        self.uploadBtn = QPushButton("&Upload data", self)
        self.testsBtn = QPushButton("&Select test", self)
        self.preferencesBtn = QPushButton("&Preferences", self)
        self.setRangeBtn = QPushButton("&Set Range", self)
        self.executeBtn = QPushButton("&Execute", self)
        self.addCurveBtn = QPushButton("&Add next curve", self)
        shutdownBtn = QPushButton("&Close the POMOKA app", self)

        self.ukladV = QVBoxLayout()
        self.ukladH = QHBoxLayout()

        self.ukladV.addWidget(self.label1)
        self.ukladV.addWidget(self.label2)
        self.ukladV.addWidget(self.resultEdt)

        self.ukladV.addWidget(self.uploadBtn)
        self.ukladH.addWidget(self.testsBtn)
        self.ukladH.addWidget(self.preferencesBtn)
        self.ukladH.addWidget(self.setRangeBtn)
        self.ukladV.addWidget(self.executeBtn)
        self.ukladH.addWidget(self.addCurveBtn)

        self.ukladV.addLayout(self.ukladH)
        self.ukladV.addWidget(shutdownBtn)

        self.setLayout(self.ukladV)

        shutdownBtn.clicked.connect(self.shutdown)
        self.uploadBtn.clicked.connect(self.uploadCSV)
        self.testsBtn.clicked.connect(self.CBtests)
        self.preferencesBtn.clicked.connect(self.CBpreferences)
        self.setRangeBtn.clicked.connect(self.setRanges)
        self.addCurveBtn.clicked.connect(self.addCurve)
        self.executeBtn.clicked.connect(self.toggleExecution)

        self.preferencesBtn.setEnabled(False)
        self.setRangeBtn.setEnabled(False)
        self.addCurveBtn.setEnabled(False)

        self.resize(400, 270)
        self.setWindowTitle("POMOKA")
        self.setWindowIcon(QIcon('icon.png'))

    def center(self):
        # pobranie wymiarów ekranu
        screen = QApplication.desktop().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # pobranie wymiarów okna
        window_size = self.geometry()
        window_width = window_size.width()
        window_height = window_size.height()

        # obliczenie pozycji X i Y
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # ustawienie geometrii okna
        self.setGeometry(x, y, window_width, window_height)
    def uploadCSV(self):  # funkcja do opcji z wgraniem pliku
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik CSV lub XLSX",
            "",
            "CSV i Excel Files (*.csv *.xlsx *.xls);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)",
            options=options
        )
        if fileName:
            self.filePathEdt.setText(fileName)
            self.askHeaderRow(fileName)

    def askHeaderRow(self, fileName):  # funkcja pytająca o header kolumne
        row, ok = QInputDialog.getInt(self, "Header Row", "Enter the row number containing column headers:", 1, 1, 100, 1)
        if ok:
            self.readCSV(fileName, row)

    def readCSV(self, fileName, headerRow):  # funkcja do wczytania csv/xlsx/xls
        try:
            if fileName.endswith('.csv'):
                df = pd.read_csv(fileName, header=headerRow-1)
            elif fileName.endswith('.xlsx') or fileName.endswith('.xls'):
                df = pd.read_excel(fileName, header=headerRow-1)
            else:
                raise ValueError("Unsupported file format")

            self.df = df
            QMessageBox.information(self, "File loaded",
                                    f"Number of rows: {df.shape[0]}\nNumber of columns: {df.shape[1]}")

            if hasattr(self, 'preferencesList'):
                self.preferencesList.clear()
                self.preferencesList.setParent(None)
                self.preferencesList.deleteLater()
                self.toggleSetRangeBtn()
                self.adjustSize()

            self.preferencesBtn.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unable to load file: {str(e)}")

    def CBtests(self):  # wybor testow
        self.testsList = QListWidget(self)
        self.testsList.setSelectionMode(QAbstractItemView.MultiSelection)

        self.testsList.addItem("Gehan-Wilcoxon test")
        self.testsList.addItem("Cox-Mantel test")
        self.testsList.addItem("F Cox test")
        self.testsList.addItem("Log-rank test")
        self.testsList.addItem("Peto-Peto-Wilcoxon test")
        self.testsList.setFixedSize(300, 75)

        default_item = self.testsList.findItems("Log-rank test", Qt.MatchExactly)[0]
        default_index = self.testsList.indexFromItem(default_item).row()
        self.testsList.setCurrentRow(default_index)

        self.ukladV.addWidget(self.testsList)
        self.testsBtn.setEnabled(False)  # dezaktywacja przycisku po dodaniu pól

    def CBpreferences(self):
        self.preferencesList = QListWidget(self)
        self.preferencesList.setSelectionMode(QAbstractItemView.MultiSelection)

        self.preferencesList.addItem("no preferences")
        if hasattr(self, 'df'):
            columns = self.df.columns
            for column in columns:
                self.preferencesList.addItem(column)

        self.preferencesList.setFixedSize(300, 75)

        self.ukladV.addWidget(self.preferencesList)
        self.preferencesBtn.setEnabled(False)  # dezaktywacja przycisku po dodaniu pól
        self.setRangeBtn.setEnabled(True)
        self.addCurveBtn.setEnabled

    def setRanges(self):

        self.selected_sex = 2
        self.selected_age_start = 0
        self.selected_age_end = 100
        self.selected_option = 2
        selected_columns = [item.text() for item in self.preferencesList.selectedItems()]

        for column in selected_columns:
            if column == "no preferences":
                continue

            values = self.df[column].unique().tolist()
            values = [str(value) for value in values]

            value_range, ok = QInputDialog.getText(self, f"Select range for {column}",
                                                   f"Enter the range for column {column} (minimum value-maximum value or specific values like 'SVG,MVG,SAG+Veins'):")
            if ok:
                try:
                    specific_values = None
                    if '-' in value_range:
                        try:
                            lower, upper = map(int, value_range.split('-'))
                            # sprawdzanie czy zakres wprowadzony przez uzytkownika jest zgodny z danymi
                            column_values = self.df[column]
                            filtered_values = column_values[(column_values >= lower) & (column_values <= upper)]

                            if filtered_values.empty:
                                QMessageBox.warning(self, "Range Error",
                                                    f"No values found in column '{column}' for the given range: {lower}-{upper}. Make sure you enter the correct format: MINIMUM value - MAXIMUM value")
                                continue

                            self.column_ranges[column] = ('numeric', (lower, upper))

                        except ValueError:
                            QMessageBox.warning(self, "Input Error", "Please enter a valid numeric range.")
                            continue
                    else:
                        specific_values = [value.strip() for value in value_range.split(',')]
                        valid_values = [value.lower() for value in values]
                        if not set([v.lower() for v in specific_values]).issubset(set(valid_values)):
                            QMessageBox.warning(self, "Range Error",
                                                f"Some values in '{value_range}' are not present in the column '{column}'. Please enter valid values like: {', '.join(valid_values)}")
                            continue

                        self.column_ranges[column] = ('categorical', specific_values)

                    # sprawdzanie wybranej płci, jak nie uzytkownik nie wybierze to bierze obydwie do wykresu
                    if column.lower() in ['sex', 'plec', 'płeć', 'pŁeć']:
                        if specific_values and len(specific_values) == 1:
                            value = specific_values[0].lower()
                            if value in ['1', 'm', 'male']:
                                self.selected_sex = 0  # 0=dane_mezczyzn
                            elif value in ['0', 'k', 'female', 'w']:
                                self.selected_sex = 1  # 1=dane_kobiet
                        else:
                            self.selected_sex = 2

                    if column.lower() in ['female', 'kobieta']:
                        if specific_values and len(specific_values) == 1:
                            value = specific_values[0].lower()
                            if value == '1':
                                self.selected_sex = 1
                            elif value == '0':
                                self.selected_sex = 0
                        else:
                            self.selected_sex = 2

                    if column.lower() in ['male', 'mezczyzna', 'mężczyzna']:
                        if specific_values and len(specific_values) == 1:
                            value = specific_values[0].lower()
                            if value == '1':
                                self.selected_sex = 0
                            elif value == '0':
                                self.selected_sex = 1
                        else:
                            self.selected_sex = 2

                    # sprawdzanie wybranego wieku, jak nie uzytkownik nie wybierze to bierze średni
                    if column.lower() in ['age', 'wiek']:
                        if specific_values and len(specific_values) == 1:
                            self.selected_age = int(specific_values[0])
                            self.selected_option = 1
                        elif len(value_range.split('-')) == 2:
                            lower, upper = map(int, value_range.split('-'))
                            if lower > upper:
                                self.selected_age_start = upper
                                self.selected_age_end = lower
                            else:
                                self.selected_age_start = lower
                                self.selected_age_end = upper
                            self.selected_option = 2

                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Please enter a valid numeric or categorical range.")
    def shutdown(self):  # zamykanie aplikacji poprzez przycisk
        self.close()

    def closeEvent(self, event):  # zapytanie przed zamknieciem aplikacji
        odp = QMessageBox.question(
            self, 'Komunikat',
            "Are you sure you want to close?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):  # ESC na klawiaturze - tez zamyka program
        if e.key() == Qt.Key_Escape:
            self.close()

    def gus(self, ax, last_time_km):  # TODO
        # dwie zmienne podawane do funkcji generujacej wykres dla jednego rocznika
        sex = self.selected_sex

        #BACKLOG jak działa:
        #self.selected_age = wiek pacjenta
        #self.selected_age_start = wiek pacjenta dolny zakres
        #self.selected_age_end = wiek pacjenta gorny zakres
        #zakres 65-70 to wtedy start = 1952, a end = 1957, a wiec z tego powodu jest to na odwrot


        # te dwie plus sex generuje wykres dla zakresu rocznikow
        opcja = self.selected_option #czyli czy generujemy wykres dla jednego rocznika czy zakresu, 2 to zakres
        file_path = 'tablice_trwania_zycia_w_latach_1990-2022.xlsx'
        file_path_men = 'dane_mezczyzni.xlsx'
        file_path_women = 'dane_kobiety.xlsx'
        if sex == 0:
            sextext = 'men'
        if sex == 1:
            sextext = 'women'
        if sex == 2:
            sextext = 'men and women'
        # tworzenie plikow jesli nie istnieja (w przyszlosci przyda sie do aktualizacji danych)
        if not os.path.exists(file_path_men) or not os.path.exists(file_path_women):
            tab_m, tab_k = prepare_data(file_path)
            save_data_to_excel(file_path_men, file_path_women, tab_m, tab_k)

        if opcja == 1:
            year = (2022 - self.selected_age)
            gus_chart = lineChartOne(sex, year)
            # pobranie osi z figury wykresu z GUS
            gus_ax = gus_chart.axes[0]

            # pobranie danych z osi wykresu GUS
            x_data = gus_ax.lines[0].get_xdata()  # Oś X (lata)
            y_data = gus_ax.lines[0].get_ydata()  # Oś Y (procenty przeżycia)

            # przekształcenie procentów przeżycia na prawdopodobieństwa (0-1)
            y_data_probability = y_data / 100

            #przycinanie osi X do dlugosci kmf
            valid_indices = x_data <= last_time_km
            self.x_data_trimmed = x_data[valid_indices]
            self.y_data_probability_trimmed = y_data_probability[valid_indices]

            # dodanie drugiej krzywej na ten sam wykres Kaplan-Meiera
            agetext = 2022 - year
            print (f'{self.selected_sex}')
            print (f'{sex}')
            ax.step(self.x_data_trimmed, self.y_data_probability_trimmed, where='post', label=f'HEALTHY (age: {agetext}; sex: {sextext})',
                    linestyle='-', color='orange')
            ax.legend()

        if opcja == 2:
            year_start = (2022 - self.selected_age_end)
            year_end = (2022 - self.selected_age_start)
            gus_chart = lineChartRange(sex, year_start, year_end)
            gus_ax = gus_chart.axes[0]

            # pobranie danych z osi wykresu GUS
            x_data = gus_ax.lines[0].get_xdata()  # Oś X (lata)
            y_data = gus_ax.lines[0].get_ydata()  # Oś Y (procenty przeżycia)

            # przekształcenie procentów przeżycia na prawdopodobieństwa (0-1)
            y_data_probability = y_data / 100

            # przycinanie osi X do dlugosci kmf
            valid_indices = x_data <= last_time_km
            self.x_data_trimmed = x_data[valid_indices]
            self.y_data_probability_trimmed = y_data_probability[valid_indices]

            #dodanie drugiej krzywej na ten sam wykres Kaplan-Meiera
            agetextstart = 2022 - year_start
            agetextend = 2022 - year_end
            ax.step(self.x_data_trimmed, self.y_data_probability_trimmed, where='post', label=f'HEALTHY (age: {agetextend}-{agetextstart}; sex: {sextext})',
                    linestyle='-', color='orange')
            ax.legend()

    def ill(self):
        if not hasattr(self, 'df'):
            QMessageBox.warning(self, "Error", "Data is not loaded.")
            return

        # wymagaj wybranie zakresu preferencji
        selected_preferences = [item.text() for item in self.preferencesList.selectedItems() if
                                item.text() != "no preferences"]

        if not selected_preferences:
            QMessageBox.warning(self, "Error", "No preferences selected.")
            return

        df_filtered = self.df.copy()

        # filtrowanie po wszystkich kolumnach wedlug set range lower/upper
        for column, (range_type, values) in self.column_ranges.items():
            if range_type == 'numeric':
                lower, upper = values
                df_filtered = df_filtered[(df_filtered[column] >= lower) & (df_filtered[column] <= upper)]
            elif range_type == 'categorical':
                df_filtered = df_filtered[df_filtered[column].isin(values)]

        if df_filtered.empty:
            QMessageBox.warning(self, "Error", "No data matching the selected ranges.")
            return

        self.filtered_patient_count = len(df_filtered)  # liczba pacjentow wzietych pod uwage do pliku
        print(f"pacjentów wziętych pod uwage: {self.filtered_patient_count}")
        # sprawdzamy, czy kolumny 'time' i 'event' istnieją
        if 'time' in df_filtered.columns:
            self.T_ill = df_filtered['time']
        else:
            # jeśli nie znajdzie 'time', prosi użytkownika o wybór kolumny
            column_names = df_filtered.columns.tolist()
            selected_column, ok = QInputDialog.getItem(self, "Select column for 'time'",
                                                       "Available columns:", column_names, 0, False)
            if ok and selected_column:
                self.T_ill = df_filtered[selected_column]
            else:
                QMessageBox.warning(self, "Error", "No column selected for 'time'.")
                return

        if 'event' in df_filtered.columns:
            self.E_ill = df_filtered['event']
        else:
            # jeśli nie znajdzie 'event', poproś użytkownika o wybór kolumny
            column_names = df_filtered.columns.tolist()
            selected_column, ok = QInputDialog.getItem(self, "Select column for 'event'",
                                                       "Available columns:", column_names, 0, False)
            if ok and selected_column:
                self.E_ill = df_filtered[selected_column]
            else:
                QMessageBox.warning(self, "Error", "No column selected for 'event'.")
                return

        kmf_ill = KaplanMeierFitter()

        fig, ax = plt.subplots(figsize=(10, 6))

        kmf_ill.fit(self.T_ill, event_observed=self.E_ill)
        last_time_km = kmf_ill.survival_function_.index[-1]

        # Tworzenie opisu dla legendy na podstawie preferencji i zakresów
        preferences_description = "; ".join([
            f"{pref}: {self.column_ranges[pref][1][0]}-{self.column_ranges[pref][1][1]}" if self.column_ranges[pref][
                                                                                                0] == 'numeric' else f"{pref}: {', '.join(self.column_ranges[pref][1])}"
            for pref in selected_preferences if pref in self.column_ranges
        ])

        kmf_ill.plot_survival_function(ax=ax, label=f'ILL ({preferences_description})')
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

        # pobieranie danych z wykresu kaplana
        self.survival_probabilities = kmf_ill.survival_function_['KM_estimate'].values
        self.time_points = kmf_ill.survival_function_.index

        ax.set_title('Chart')
        ax.set_xlabel('Time')
        ax.set_ylabel('Survival Probability')

        plt.grid(True)

        self.gus(ax, last_time_km)

        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.setParent(None)

        self.canvas = FigureCanvas(fig)
        self.ukladV.addWidget(self.canvas, 1, Qt.AlignBottom)
        self.canvas.draw()

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.output_dir = os.path.join("plots", timestamp)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.canvas.figure.savefig(os.path.join(self.output_dir, f"full_plot.png"))

        self.resize(self.width() + 300, self.height() + 400)
        self.center()
    def addCurve(self):
        if not hasattr(self, 'df'):
            QMessageBox.warning(self, "Error", "Data is not loaded.")
            return

        selected_preferences = [item.text() for item in self.preferencesList.selectedItems() if
                                item.text() != "no preferences"]

        if not selected_preferences:
            QMessageBox.warning(self, "Error", "No preferences selected.")
            return

        df_filtered = self.df.copy()

        for column, (range_type, values) in self.column_ranges.items():
            if range_type == 'numeric':
                lower, upper = values
                df_filtered = df_filtered[(df_filtered[column] >= lower) & (df_filtered[column] <= upper)]
            elif range_type == 'categorical':
                df_filtered = df_filtered[df_filtered[column].isin(values)]

        if df_filtered.empty:
            QMessageBox.warning(self, "Error", "No data matching the selected ranges.")
            return

        self.filtered_patient_count = len(df_filtered)
        print(f"Additional curve - patients considered: {self.filtered_patient_count}")

        if 'time' in df_filtered.columns:
            T_additional = df_filtered['time']
        else:
            column_names = df_filtered.columns.tolist()
            selected_column, ok = QInputDialog.getItem(self, "Select column for 'time'",
                                                       "Available columns:", column_names, 0, False)
            if ok and selected_column:
                T_additional = df_filtered[selected_column]
            else:
                QMessageBox.warning(self, "Error", "No column selected for 'time'.")
                return

        if 'event' in df_filtered.columns:
            E_additional = df_filtered['event']
        else:
            column_names = df_filtered.columns.tolist()
            selected_column, ok = QInputDialog.getItem(self, "Select column for 'event'",
                                                       "Available columns:", column_names, 0, False)
            if ok and selected_column:
                E_additional = df_filtered[selected_column]
            else:
                QMessageBox.warning(self, "Error", "No column selected for 'event'.")
                return

        kmf_additional = KaplanMeierFitter()

        if not hasattr(self, 'canvas') or self.canvas is None:
            QMessageBox.warning(self, "Error", "No existing plot to add a curve.")
            return

        ax = self.canvas.figure.axes[0]

        predefined_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        existing_lines = len(ax.lines)
        if existing_lines >= len(predefined_colors):
            QMessageBox.warning(self, "Error", "No more unique colors available.")
            return

        selected_color = predefined_colors[existing_lines]

        # Tworzenie opisu dla legendy na podstawie preferencji i zakresów
        preferences_description = "; ".join([
            f"{pref}: {self.column_ranges[pref][1][0]}-{self.column_ranges[pref][1][1]}" if self.column_ranges[pref][
                                                                                                0] == 'numeric' else f"{pref}: {', '.join(self.column_ranges[pref][1])}"
            for pref in selected_preferences if pref in self.column_ranges
        ])

        kmf_additional.fit(T_additional, event_observed=E_additional)
        kmf_additional.plot_survival_function(ax=ax, label=f'ILL ({preferences_description})', color=selected_color)
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
        self.canvas.draw()

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        if not hasattr(self, 'output_dir'):
            self.output_dir = os.path.join("plots", timestamp)
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

        self.canvas.figure.savefig(os.path.join(self.output_dir, f"updated_plot_{existing_lines + 1}.png"))
        self.preferencesList.close()
        self.preferencesList.clearSelection()
        self.preferencesBtn.setEnabled(True)
        self.preferencesList.setEnabled(True)
        self.setRangeBtn.setEnabled(True)
        self.column_ranges = {}

    def run_gehan_wilcoxon(self):  # TODO
        self.survival_gus_interpolated = np.interp(self.time_points, self.x_data_trimmed, self.y_data_probability_trimmed)

        print(f"T_ill type: {type(self.time_points)}, value: {self.time_points}")
        print(f"x_data_trimmed type: {type(self.x_data_trimmed)}, value: {self.x_data_trimmed}")
        print(f"y_data_trimmed type: {type(self.y_data_probability_trimmed)}, value: {self.y_data_probability_trimmed}")
        print(f"self.survival_gus_interpolated: {type(self.survival_gus_interpolated)}, value: {self.survival_gus_interpolated}")
        print(f"E_ill type: {type(self.survival_probabilities)}, value: {self.survival_probabilities}")
        print(f"E_ill type: {type(self.T_ill)}, value: {self.survival_probabilities}")
        #time = list(self.T_ill) + list(self.x_data_trimmed)
        #event = list(self.E_ill) + list(self.y_data_probability_trimmed)
        #group = ['ill'] * len(self.T_ill) + ['gus'] * len(self.x_data_trimmed)

        time = list(self.time_points) + list(self.time_points)
        event = list(self.survival_probabilities) + list(self.survival_gus_interpolated)
        group = ['ill'] * len(self.time_points) + ['gus'] * len(self.time_points)

        data = pd.DataFrame({
            'time': time,
            'event': event,
            'group': group
        })

        result = multivariate_logrank_test(data['time'], data['group'], data['event'], weightings="wilcoxon")

        self.resultEdt.setText(f"Gehan-Wilcoxon test: Z-statystyka = {result.test_statistic}, p-wartość = {result.p_value}")
        text = (f"Gehan-Wilcoxon test: Z-statystyka = {result.test_statistic}, p-wartość = {result.p_value}")
        self.time(text)
        QMessageBox.information(self, "Gehan-Wilcoxon test", "Wykonano test Gehan-Wilcoxon, kliknij OK aby przejść do wyniku kolejnego testu")

    def run_cox_mantel(self):  # TODO
        result = "in progress"
        self.resultEdt.setText(f"Cox-Mantel test: Chi2 = {result}, p-wartość = {result}")
        QMessageBox.information(self, "Cox-Mantel test", "Wykonano test Cox-Mantel, kliknij OK aby przejść do wyniku kolejnego testu")

    def run_f_cox(self):  # TODO
        result = "in progress"
        self.resultEdt.setText(f"F Cox test: F-statystyka = {result}, p-wartość = {result}")
        QMessageBox.information(self, "F Cox test", "Wykonano test F Cox, kliknij OK aby przejść do wyniku kolejnego testu")

    def run_log_rank(self):
        result = logrank_test(self.T_ill, self.x_data_trimmed, event_observed_A=self.E_ill, event_observed_B=self.y_data_probability_trimmed)
        self.resultEdt.setText(f"Log-rank test: Z-statystyka = {result.test_statistic}, p-wartość = {result.p_value}")
        text = (f"Log-rank test: Z-statystyka = {result.test_statistic}, p-wartość = {result.p_value}")
        self.time(text)
        QMessageBox.information(self, "Log-rank test", "Wykonano test Log-rank, kliknij OK aby przejść do wyniku kolejnego testu")

    def run_peto_peto_wilcoxon(self):  # TODO
        result = "in progress"
        self.resultEdt.setText(f"Peto-Peto-Wilcoxon test: Z-statystyka = {result}, p-wartość = {result}")
        QMessageBox.information(self, "Peto-Peto-Wilcoxon test", "Wykonano test Peto-Peto-Wilcoxon, kliknij OK aby przejść do wyniku kolejnego testu")

    def time(self, text):
        filename = os.path.join(self.output_dir, f"test_result.txt")
        with open(filename, "w") as file:
            file.write(text)
            file.write(f"\nfor the ill curve was used {self.filtered_patient_count} patients")

    def toggleExecution(self):
        if self.isExecuting:
            self.breakExecution()
        else:
            self.startExecution()

    def startExecution(self):
        if not hasattr(self, 'testsList') or self.testsList is None or not self.testsList.selectedItems():
            QMessageBox.warning(self, "Warning", "Please select a statistical test.")
            return

            # Sprawdź, czy preferencesList istnieje i jest poprawnym widgetem
        if not hasattr(self, 'preferencesList') or self.preferencesList is None:
            QMessageBox.warning(self, "Warning", "Preferences list is missing or invalid.")
            return

            # Próbuj odczytać selectedItems() tylko, jeśli preferencesList nie zostało usunięte
        try:
            if not self.preferencesList.selectedItems():
                QMessageBox.warning(self, "Warning", "Please select preferences or 'no preferences' when not needed.")
                return
        except RuntimeError:
            QMessageBox.warning(self, "Warning", "Preferences list has been deleted.")
            return

        for index in range(self.preferencesList.count()):
            item = self.preferencesList.item(index)
            if item.isSelected() and item.text() != "no preferences" and item.text() not in self.column_ranges:
                QMessageBox.warning(self, "Warning", f"Please set range for {item.text()} before executing.")
                return
        self.testsBtn.setEnabled(False)
        self.setRangeBtn.setEnabled(False)
        self.preferencesBtn.setEnabled(False)

        self.uploadBtn.setEnabled(False)
        self.addCurveBtn.setEnabled(True)
        if hasattr(self, 'testsList') and self.testsList.isVisible():
            self.testsList.setEnabled(False)
        if hasattr(self, 'preferencesList') and self.preferencesList.isVisible():
            self.preferencesList.setEnabled(False)
        self.executeBtn.setText("Break")
        self.isExecuting = True

        self.ill()
        self.preferencesList.close()
        self.preferencesList.clearSelection()
        self.preferencesBtn.setEnabled(True)
        self.preferencesList.setEnabled(True)
        self.setRangeBtn.setEnabled(True)
        self.column_ranges = {}
        selected_tests = [item.text() for item in self.testsList.selectedItems()]
        for test in selected_tests:
            if test == "Gehan-Wilcoxon test":
                self.run_gehan_wilcoxon()
            elif test == "Cox-Mantel test":
                self.run_cox_mantel()
            elif test == "F Cox test":
                self.run_f_cox()
            elif test == "Log-rank test":
                self.run_log_rank()
            elif test == "Peto-Peto-Wilcoxon test":
                self.run_peto_peto_wilcoxon()

    def breakExecution(self):
        for i in reversed(range(self.ukladV.count())):
            widget = self.ukladV.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                widget.setParent(None)
                self.resize(self.width() - 300, self.height() - 400)
                self.center()

        self.executeBtn.setText("Execute")
        self.isExecuting = False
        if hasattr(self, 'testsList') and self.testsList.isVisible():
            self.testsList.setEnabled(True)
        else:
            self.testsBtn.setEnabled(True)
        if hasattr(self, 'preferencesList') and self.preferencesList.isVisible():
            self.preferencesList.setEnabled(True)
            self.setRangeBtn.setEnabled(True)
        else:
            self.preferencesBtn.setEnabled(True)
        self.uploadBtn.setEnabled(True)

    def toggleSetRangeBtn(self):
        if self.preferencesList.isVisible():
            self.setRangeBtn.setEnabled(True)
        else:
            self.setRangeBtn.setEnabled(False)

class POMOKAstartup(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("POMOKA menu")
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet("background-color: lightgrey;")
        self.resize(500, 270)

        self.label = QLabel("<b>Welcome to POMOKA<b>", self)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.label.setStyleSheet("font-size: 20px; margin-top: 5px;")

        self.statBtn = QPushButton("POMOKA stat", self)
        self.modelBtn = QPushButton("POMOKA model (in progress)", self)
        button_style = (
            "background-color: white; border: 2px solid #000; border-radius: 10px; font-size: 14px; padding: 25px; width: 400px;"
        )
        self.statBtn.setStyleSheet(button_style)
        self.modelBtn.setStyleSheet(button_style)
        self.modelBtn.setEnabled(False)

        self.statBtn.clicked.connect(self.openMainApp)

        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignTop)
        layout.addStretch()
        layout.addWidget(self.statBtn, alignment=Qt.AlignCenter)
        layout.addWidget(self.modelBtn, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def openMainApp(self):
        self.mainApp = POMOKAstat()
        self.mainApp.show()
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    startup = POMOKAstartup()
    startup.show()
    app.exec_()
