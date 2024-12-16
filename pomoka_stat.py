import os
import sys
from datetime import datetime

# PyQt5 imports
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout,
    QVBoxLayout, QFileDialog, QAbstractItemView, QListWidget, QInputDialog, QDialog, QVBoxLayout, QCheckBox, QComboBox)
from PySide6.QtGui import QIcon, QPalette, QColor, QGuiApplication
from PySide6.QtCore import Qt

# Data handling and analysis
import pandas as pd
import numpy as np
import re
from scipy import stats
from scipy.interpolate import interp1d
#from numpy import trapz
from scipy.stats import mannwhitneyu

# Matplotlib for plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patheffects import withStroke

# Lifelines for survival analysis
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test #(delete when new tests come in)
from scipy.stats import ks_2samp

# Custom imports
from plot_gus import prepare_data, save_data_to_excel, lineChartOne, lineChartRange

from fpdf import FPDF


class TestResultsStorage:
    def __init__(self):
        self.results = {}  # Struktura: {"Test_Name": {"Curve_ID": {"Metric": value}}}

    def add_result(self, test_name, curve_id, result_dict):
        if test_name not in self.results:
            self.results[test_name] = {}
        self.results[test_name][curve_id] = result_dict

    def get_result(self, test_name, curve_id):
        return self.results.get(test_name, {}).get(curve_id, None)

    def get_all_results(self):
        return self.results

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QCheckBox, QPushButton, QLabel

class ReportOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report Options")

        self.layout = QVBoxLayout(self)

        # Input for report name
        self.reportNameLabel = QLabel("Enter report name:")
        self.reportNameInput = QLineEdit(self)
        self.layout.addWidget(self.reportNameLabel)
        self.layout.addWidget(self.reportNameInput)

        # Checkbox for saving chart separately
        self.saveChartCheckbox = QCheckBox("Save chart as a separate file")
        self.layout.addWidget(self.saveChartCheckbox)

        # Buttons
        self.okButton = QPushButton("OK", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        self.layout.addWidget(self.okButton)
        self.layout.addWidget(self.cancelButton)

    def getOptions(self):
        return {
            "report_name": self.reportNameInput.text().strip(),
            "save_chart_separately": self.saveChartCheckbox.isChecked(),
        }


class ChartEditorDialog(QWidget):
    def __init__(self, figure, parent=None):
        super().__init__(parent)
        self.figure = figure  # Przekazujemy obiekt wykresu
        self.original_colors = []  # Przechowuje oryginalne kolory linii
        self.original_styles = []  # Przechowuje oryginalne style linii
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Chart Editor")
        layout = QVBoxLayout()

        # Sekcja czcionki osi
        font_label = QLabel("Set Axis Font Size:")
        self.font_input = QLineEdit(self)
        self.font_input.setPlaceholderText("Enter font size (e.g., 12)")
        layout.addWidget(font_label)
        layout.addWidget(self.font_input)

        font_apply_btn = QPushButton("Apply Font Size", self)
        font_apply_btn.clicked.connect(self.applyFontSize)
        layout.addWidget(font_apply_btn)

        # Sekcja tytułu wykresu
        title_label = QLabel("Chart Title:")
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Enter chart title (e.g., My Chart)")
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)

        self.title_checkbox = QPushButton("Toggle Chart Title", self)
        self.title_checkbox.clicked.connect(self.toggleTitle)
        layout.addWidget(self.title_checkbox)

        # Sekcja osi Y
        y_axis_label = QLabel("Y-axis Title:")
        self.y_axis_input = QLineEdit(self)
        self.y_axis_input.setPlaceholderText("Enter Y-axis title")
        layout.addWidget(y_axis_label)
        layout.addWidget(self.y_axis_input)

        self.add_y_axis_btn = QPushButton("Add Y Axis Title", self)
        self.add_y_axis_btn.clicked.connect(self.addYAxis)
        layout.addWidget(self.add_y_axis_btn)

        self.remove_y_axis_btn = QPushButton("Remove Y Axis Title", self)
        self.remove_y_axis_btn.clicked.connect(self.removeYAxis)
        layout.addWidget(self.remove_y_axis_btn)

        # Sekcja osi X
        x_axis_label = QLabel("X-axis Title:")
        self.x_axis_input = QLineEdit(self)
        self.x_axis_input.setPlaceholderText("Enter X-axis title")
        layout.addWidget(x_axis_label)
        layout.addWidget(self.x_axis_input)

        self.add_x_axis_btn = QPushButton("Add X Axis Title", self)
        self.add_x_axis_btn.clicked.connect(self.addXAxis)
        layout.addWidget(self.add_x_axis_btn)

        self.remove_x_axis_btn = QPushButton("Remove X Axis Title", self)
        self.remove_x_axis_btn.clicked.connect(self.removeXAxis)
        layout.addWidget(self.remove_x_axis_btn)

        # Sekcja legendy
        legend_label = QLabel("Legend:")
        self.toggle_legend_btn = QPushButton("Toggle Legend", self)
        self.toggle_legend_btn.clicked.connect(self.toggleLegend)
        layout.addWidget(legend_label)
        layout.addWidget(self.toggle_legend_btn)

        # Sekcja stylów
        style_label = QLabel("Style:")
        self.black_white_btn = QPushButton("Set Black & White Style", self)
        self.black_white_btn.clicked.connect(self.setBlackAndWhiteStyle)
        layout.addWidget(style_label)
        layout.addWidget(self.black_white_btn)

        self.color_btn = QPushButton("Restore Original Style", self)
        self.color_btn.clicked.connect(self.restoreColorStyle)
        layout.addWidget(self.color_btn)

        # Zamknięcie okna
        close_btn = QPushButton("Close Chart Editor", self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def toggleTitle(self):
        """Włącz lub wyłącz tytuł wykresu."""
        for ax in self.figure.axes:
            ax.set_title('' if ax.get_title() else self.title_input.text())
        self.figure.canvas.draw()

    def applyFontSize(self):
        """Zastosuj rozmiar czcionki do osi."""
        font_size = self.font_input.text()
        if font_size.isdigit():
            font_size = int(font_size)
            for ax in self.figure.axes:
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontsize(font_size)
            self.figure.canvas.draw()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a valid font size.")

    def toggleAxisTitles(self):
        """Włącz lub wyłącz tytuły osi."""
        for ax in self.figure.axes:
            if ax.get_xlabel() or ax.get_ylabel():
                ax.set_xlabel('')
                ax.set_ylabel('')
            else:
                ax.set_xlabel(self.x_axis_input.text())
                ax.set_ylabel(self.y_axis_input.text())
        self.figure.canvas.draw()

    def toggleLegend(self):
        """Włącz lub wyłącz legendę."""
        for ax in self.figure.axes:
            legend = ax.get_legend()
            if legend:
                legend.remove()
            else:
                ax.legend()
        self.figure.canvas.draw()

    def setBlackAndWhiteStyle(self):
        """Ustawia tryb czarno-biały na wykresie i aktualizuje legendę."""
        self.original_colors = [line.get_color() for ax in self.figure.axes for line in ax.get_lines()]
        self.original_styles = [line.get_linestyle() for ax in self.figure.axes for line in ax.get_lines()]
        line_styles = ['-', '--', '-.', ':', (0, (5, 10)), (0, (5, 1)), (0, (3, 5, 1, 5)), (0, (1, 1))]  # Różne style linii
        for ax in self.figure.axes:
            for idx, line in enumerate(ax.get_lines()):
                line.set_color("black")
                line.set_linestyle(line_styles[idx % len(line_styles)])  # Unikalny styl linii dla każdej krzywej
            ax.legend()  # Aktualizuj legendę
        self.figure.canvas.draw()

    def restoreColorStyle(self):
        """Przywraca kolorowy styl wykresu i aktualizuje legendę."""
        if not self.original_colors or not self.original_styles:
            QMessageBox.warning(self, "Error", "Original styles or colors are not stored!")
            return
        i = 0
        for ax in self.figure.axes:
            for line in ax.get_lines():
                if i < len(self.original_colors) and i < len(self.original_styles):
                    line.set_color(self.original_colors[i])  # Przywraca oryginalny kolor
                    line.set_linestyle(self.original_styles[i])  # Przywraca oryginalny styl
                    i += 1
            ax.legend()  # Aktualizuj legendę
        self.figure.canvas.draw()

    def addXAxis(self):
        """Dodaje etykiety na osi X."""
        for ax in self.figure.axes:
            ax.set_xlabel(self.x_axis_input.text() or "X Axis")
        self.figure.canvas.draw()

    def removeXAxis(self):
        """Usuwa etykiety z osi X."""
        for ax in self.figure.axes:
            ax.set_xlabel('')
        self.figure.canvas.draw()

    def addYAxis(self):
        """Dodaje etykiety na osi Y."""
        for ax in self.figure.axes:
            ax.set_ylabel(self.y_axis_input.text() or "Y Axis")
        self.figure.canvas.draw()

    def removeYAxis(self):
        """Usuwa etykiety z osi Y."""
        for ax in self.figure.axes:
            ax.set_ylabel('')
        self.figure.canvas.draw()

    def close(self):
        """Zamyka okno dialogowe."""
        self.hide()

class POMOKAstat(QWidget):
    global_iteration_offset = 0
    is_first_call = True
    def __init__(self, parent=None):
        super().__init__(parent)
        self.survival_probabilities_ill = None
        self.time_points_ill = None
        self.interface()
        self.isExecuting = False
        self.column_ranges = {}
        self.curves_data = []
        self.legend_text = []
        self.results_storage = TestResultsStorage()

    def interface(self):  # interface apki
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#ECECED"))
        self.setPalette(palette)

        self.label1 = QLabel("<b>Be sure to read the detailed instructions for using the program!<b>", self)
        self.label2 = QLabel("<b>Results:<b>", self)

        self.filePathEdt = QLineEdit()
        self.resultEdt = QLineEdit()
        self.resultEdt.setReadOnly(True)

        self.uploadBtn = QPushButton("&Upload data", self)
        self.setRangeBtn = QPushButton("&Set Range", self)
        self.executeBtn = QPushButton("&Execute", self)
        self.addCurveBtn = QPushButton("&Add next curve", self)
        self.generateReportBtn = QPushButton("&Generate Report", self)
        self.editChartBtn = QPushButton("&Edit Chart", self)
        shutdownBtn = QPushButton("&Close the POMOKA app", self)

        # Styl przycisków
        common_button_style = """
            QPushButton {
                color: black;            /* Kolor tekstu */
                background-color: white; /* Tło prostokąta */
                border: 1px solid black; /* Ramka prostokąta */
                padding: 3px;            /* Wewnętrzny margines */
                border-radius: 5px;      /* Zaokrąglone rogi */
            }
            QPushButton:hover {
                background-color: #f0f0f0; /* Jaśniejsze tło po najechaniu */
            }
            QPushButton:pressed {
                background-color: #e0e0e0; /* Jeszcze ciemniejsze tło po kliknięciu */
            }
            QPushButton:disabled {
                background-color: #f5f5f5; /* Subtelne jasnoszare tło dla wyłączonego przycisku */
                color: #b0b0b0;            /* Delikatnie wyblakły tekst */
                border: 2px solid #d0d0d0; /* Subtelna ramka */
            }
        """
        self.uploadBtn.setStyleSheet(common_button_style)
        self.setRangeBtn.setStyleSheet(common_button_style)
        self.executeBtn.setStyleSheet(common_button_style)
        self.addCurveBtn.setStyleSheet(common_button_style)
        self.generateReportBtn.setStyleSheet(common_button_style)
        self.editChartBtn.setStyleSheet(common_button_style)
        shutdownBtn.setStyleSheet(common_button_style)

        # Układ przycisków
        self.ukladV = QVBoxLayout()
        self.ukladH = QHBoxLayout()

        self.ukladV.addWidget(self.label1)

        # Sekcja dla wyników
        horizontalLayoutForLabel2AndResult = QHBoxLayout()
        horizontalLayoutForLabel2AndResult.addWidget(self.label2)
        self.resultEdt.setStyleSheet("""
            QLineEdit {
                color: black;            /* Kolor tekstu */
                background-color: white; /* Tło prostokąta */
                border: 1px solid black; /* Ramka prostokąta */
                padding: 3px;            /* Wewnętrzny margines */
                border-radius: 5px;      /* Zaokrąglone rogi */
            }
        """)
        horizontalLayoutForLabel2AndResult.addWidget(self.resultEdt)
        self.ukladV.addLayout(horizontalLayoutForLabel2AndResult)

        # Dodanie przycisków do układu
        self.ukladV.addWidget(self.uploadBtn)
        self.ukladH.addWidget(self.setRangeBtn)
        self.ukladV.addWidget(self.executeBtn)
        self.ukladH.addWidget(self.addCurveBtn)
        self.ukladV.addLayout(self.ukladH)
        self.ukladV.addWidget(self.generateReportBtn)
        self.ukladV.addWidget(self.editChartBtn)

        self.ukladV.addWidget(shutdownBtn)

        self.setLayout(self.ukladV)

        # Połączenia sygnałów z funkcjami
        shutdownBtn.clicked.connect(self.shutdown)
        self.uploadBtn.clicked.connect(self.uploadCSV)
        self.setRangeBtn.clicked.connect(self.setRanges)
        self.addCurveBtn.clicked.connect(self.addCurve)
        self.executeBtn.clicked.connect(self.toggleExecution)
        self.generateReportBtn.clicked.connect(self.generateReport)
        self.editChartBtn.clicked.connect(self.openEditChartWindow)

        # Ustawienia początkowe
        self.setRangeBtn.setEnabled(False)
        self.addCurveBtn.setEnabled(False)
        self.generateReportBtn.setEnabled(False)
        self.editChartBtn.setEnabled(False)

        self.resize(600, 270)
        self.setWindowTitle("POMOKA")
        self.setWindowIcon(QIcon('images/icon.png'))

    def center(self):
        # Pobranie głównego ekranu
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Pobranie wymiarów okna
        window_size = self.geometry()
        window_width = window_size.width()
        window_height = window_size.height()

        # Obliczenie pozycji X i Y
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Ustawienie geometrii okna
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
        row, ok = QInputDialog.getInt(self, "Header Row", "Enter the row number containing column headers:", 1, 1, 100,
                                      1)
        if ok:
            if self.verifyHeaderRow(fileName, row):
                self.readCSV(fileName, row)
            else:
                QMessageBox.warning(self, "Warning",
                                    "The selected row does not seem to contain valid headers. Please try again.")

    def verifyHeaderRow(self, fileName, headerRow):  # funkcja weryfikująca nagłówki
        try:
            if fileName.endswith('.csv'):
                df = pd.read_csv(fileName, header=headerRow - 1, nrows=10)  # wczytujemy tylko kilka pierwszych wierszy
            elif fileName.endswith('.xlsx') or fileName.endswith('.xls'):
                df = pd.read_excel(fileName, header=headerRow - 1, nrows=10)
            else:
                raise ValueError("Unsupported file format")

            headers = df.columns.tolist()
            if all(isinstance(header, str) and header.strip() != "" for header in headers):
                return True
            else:
                return False
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unable to verify header row: {str(e)}")
            return False

    def readCSV(self, fileName, headerRow):  # funkcja do wczytania csv/xlsx/xls
        try:
            if fileName.endswith('.csv'):
                df = pd.read_csv(fileName, header=headerRow - 1)
            elif fileName.endswith('.xlsx') or fileName.endswith('.xls'):
                df = pd.read_excel(fileName, header=headerRow - 1)
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
                #self.adjustSize()

            self.executeBtn.setEnabled(True)
            self.CBpreferences()
            self.CBtests()
            self.uploadBtn.setEnabled(False)
            self.center()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unable to load file: {str(e)}")

    def CBtests(self):  # wybor testow
        if hasattr(self, 'testsList') and self.testsList is not None:
            self.testsList.deleteLater()
            self.testsList = None

        self.testsList = QListWidget(self)
        self.testsList.setSelectionMode(QAbstractItemView.MultiSelection)

        self.testsList.addItem("Mann-Whitney U test")
        self.testsList.addItem("AUC")
        self.testsList.addItem("AUC Interpolated")
        self.testsList.addItem("Kolomorow Smirnow")
        self.testsList.addItem("Kolomorow Smirnow Interpolated")
        self.testsList.addItem("Srednia roznica interpolated")
        #self.testsList.addItem("Gehan-Wilcoxon test")
        #self.testsList.addItem("Cox-Mantel test")
        #self.testsList.addItem("F Cox test")
        #self.testsList.addItem("Log-rank test")
        #self.testsList.addItem("Peto-Peto-Wilcoxon test")
        self.testsList.setFixedSize(300, 75)

        default_item = self.testsList.findItems("Mann-Whitney U test", Qt.MatchExactly)[0]
        default_index = self.testsList.indexFromItem(default_item).row()
        self.testsList.setCurrentRow(default_index)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.preferencesList)
        horizontalLayout.addWidget(self.testsList)
        common_style = """
                    QListWidget {
                        color: black;            /* Kolor tekstu */
                        background-color: white; /* Tło prostokąta */
                        border: 1px solid black; /* Ramka prostokąta */
                        padding: 3px;           /* Wewnętrzny margines */
                        border-radius: 5px;      /* Zaokrąglone rogi */
                    }
                    QListWidget::item {
                        padding: 3px;           /* Wewnętrzny margines elementów */
                    }
                    QListWidget::item:selected {
                        background-color: lightblue; /* Tło wybranego elementu */
                        color: black;               /* Kolor tekstu wybranego elementu */
                    }
                    QListWidget:disabled {
                        background-color: #f5f5f5; /* Subtelne jasnoszare tło dla wyłączonego przycisku */
                        color: #b0b0b0;            /* Delikatnie wyblakły tekst */
                        border: 2px solid #d0d0d0; /* Subtelna ramka */
                    }
                """
        self.preferencesList.setStyleSheet(common_style)
        self.testsList.setStyleSheet(common_style)
        self.ukladV.addLayout(horizontalLayout)
        self.center()


    def CBpreferences(self):
        self.preferencesList = QListWidget(self)
        self.preferencesList.setSelectionMode(QAbstractItemView.MultiSelection)

        self.preferencesList.addItem("no preferences")
        if hasattr(self, 'df'):
            columns = self.df.columns
            for column in columns:
                self.preferencesList.addItem(column)

        self.preferencesList.setFixedSize(300, 75)
        self.selected_sex = 2
        self.selected_age_start = 0
        self.selected_age_end = 100
        self.selected_option = 2


        self.setRangeBtn.setEnabled(True)
        self.addCurveBtn.setEnabled

    def setRanges(self):
        self.selected_sex = 2
        self.selected_age_start = 0
        self.selected_age_end = 100
        self.selected_option = 2
        self.column_ranges = {}

        # Retrieve selected columns from preferences
        selected_columns = [item.text() for item in self.preferencesList.selectedItems()]

        for column in selected_columns:
            if column == 'no preferences':
                continue

            values = self.df[column].unique().tolist()
            values = [str(value) for value in values]

            while True:  # Loop to allow retry on invalid input
                value_range, ok = QInputDialog.getText(
                    self,
                    f"Select range for {column}",
                    f"Enter the range for column {column} (e.g., '1-10' or 'SVG,MVG'):"
                )

                if not ok:
                    break  # Exit if user cancels the dialog

                try:
                    # Check if input is a numeric range (e.g., "1-10")
                    if '-' in value_range:
                        # Ensure the format is strictly numeric (e.g., "min-max")
                        if not re.match(r"^\d+-\d+$", value_range.strip()):
                            QMessageBox.warning(
                                self,
                                "Format Error",
                                f"Invalid range format for column '{column}'. Please enter a valid numeric range: MINIMUM-MAXIMUM."
                            )
                            continue

                        lower, upper = map(int, value_range.split('-'))

                        # Check if lower bound is less than or equal to upper bound
                        if lower > upper:
                            QMessageBox.warning(
                                self,
                                "Range Error",
                                f"Invalid range: the lower bound ({lower}) cannot be greater than the upper bound ({upper})."
                            )
                            continue

                        column_values = self.df[column]

                        # Filter values in the range
                        filtered_values = column_values[(column_values >= lower) & (column_values <= upper)]

                        if filtered_values.empty:
                            QMessageBox.warning(
                                self,
                                "Range Error",
                                f"No values found in column '{column}' for the range: {lower}-{upper}."
                            )
                            continue

                        # Handle special cases for specific columns (e.g., age, sex)
                        if column.lower() in ['age', 'wiek']:
                            if lower == upper:
                                self.selected_age = lower
                                self.selected_option = 1
                            else:
                                self.selected_age_start = lower
                                self.selected_age_end = upper
                                self.selected_option = 2

                        if column.lower() in ['sex', 'plec', 'płeć', 'pŁeć']:
                            value = 2
                            if lower == upper:
                                value = lower
                                if value in [1, 'm', 'male']:
                                    self.selected_sex = 0  # 0=dane_mezczyzn
                                elif value in [0, 'k', 'female', 'w', 'f']:
                                    self.selected_sex = 1  # 1=dane_kobiet
                                else:
                                    self.selected_sex = 2

                        self.column_ranges[column] = ('numeric', (lower, upper))
                        break

                    # Check if input is a comma-separated list of values (e.g., "SVG,MVG")
                    elif ',' in value_range or value_range.strip():
                        value_list = [val.strip() for val in value_range.split(',')]

                        # Verify if all entered values exist in the column
                        if not set(value_list).issubset(set(values)):
                            QMessageBox.warning(
                                self,
                                "Value Error",
                                f"Some values in '{value_range}' do not exist in column '{column}'."
                            )
                            continue

                        self.column_ranges[column] = ('categorical', value_list)
                        break

                    else:
                        QMessageBox.warning(
                            self,
                            "Input Error",
                            "Please enter a valid range (e.g., 'MINIMUM-MAXIMUM' or 'value1,value2,...')."
                        )
                        continue

                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Input Error",
                        "Invalid input. Please enter a valid numeric range or a comma-separated list of values."
                    )

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
        ##DEBUG
        print("=== DEBUG: START OF FUNCTION 'gus' ===")
        print(f"Selected sex: {self.selected_sex}")
        #print(f"Selected age: {self.selected_age}")
        print(f"Selected age start: {self.selected_age_start}")
        print(f"Selected age end: {self.selected_age_end}")
        print(f"Selected option: {self.selected_option}")
        print(f"Last time KM: {last_time_km}")
        print("=====================================")

        sex = self.selected_sex

        #BACKLOG jak działa:
        #self.selected_age = wiek pacjenta
        #self.selected_age_start = wiek pacjenta dolny zakres
        #self.selected_age_end = wiek pacjenta gorny zakres
        #zakres 65-70 to wtedy start = 1952, a end = 1957, a wiec z tego powodu jest to na odwrot


        # te dwie plus sex generuje wykres dla zakresu rocznikow
        opcja = self.selected_option #czyli czy generujemy wykres dla jednego rocznika czy zakresu, 2 to zakres
        file_path = 'data/tablice_trwania_zycia_w_latach_1990-2022.xlsx'
        file_path_men = 'data/dane_mezczyzni.xlsx'
        file_path_women = 'data/dane_kobiety.xlsx'
        file_path_all = 'data/dane_ogolne.xlsx'
        print(f"koncowy_gus:{self.selected_sex}")
        if sex == 0:
            sextext = 'men'
        if sex == 1:
            sextext = 'women'
        if sex == 2:
            sextext = 'men and women'
        # tworzenie plikow jesli nie istnieja (w przyszlosci przyda sie do aktualizacji danych)
        if not os.path.exists(file_path_men) or not os.path.exists(file_path_women) or not os.path.exists(file_path_all):
            tab_m, tab_k = prepare_data(file_path)
            save_data_to_excel(file_path_men, file_path_women, file_path_all, tab_m, tab_k)

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
            ax.step(self.x_data_trimmed, self.y_data_probability_trimmed, where='post',
                    label=f'HEALTHY (age: {agetext}; sex: {sextext})',
                    linestyle='-', color='orange')
            self.guslegend = f'HEALTHY (age: {agetext}; sex: {sextext})'
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
            ax.step(self.x_data_trimmed, self.y_data_probability_trimmed, where='post',
                    label=f'HEALTHY (age: {agetextend}-{agetextstart}; sex: {sextext})',
                    linestyle='-', color='orange')
            self.guslegend = f'HEALTHY (age: {agetextend}-{agetextstart}; sex: {sextext})'
            ax.legend()
    def update_legend_widget(self):
        if not hasattr(self, 'text_widget'):
            self.text_widget = QLabel()

        self.text_widget.hide()
        self.text_widget = QLabel()
        predefined_colors = [
            '#1f77b4',  # niebieski
            '#ff7f0e',  # pomarańczowy
            '#2ca02c',  # zielony
            '#d62728',  # czerwony
            '#9467bd',  # fioletowy
            '#8c564b',  # brązowy
            '#e377c2',  # różowy
            '#7f7f7f',  # szary
        ]
        row_text_1_1 = (f'<span style="color: #ff7f0e;">&#8212;</span> {self.guslegend} ')
        row_text_1_2 = (f'<span style="color: #1f77b4;">&#8212;</span> {self.legend_text[0]}')
        if self.legend_text and len(self.legend_text) > 1 and self.legend_text[1] != "":
            row_text_2_1 = (f'<br><span style="color: #2ca02c;">&#8212;</span> {self.legend_text[1]} ')
        else:
            row_text_2_1 = ''
        if self.legend_text and len(self.legend_text) > 2 and self.legend_text[2] != "":
            row_text_2_2 = (f'<span style="color: #d62728;">&#8212;</span> {self.legend_text[2]}')
        else:
            row_text_2_2 = ''
        if self.legend_text and len(self.legend_text) > 3 and self.legend_text[3] != "":
            row_text_3_1 = (f'<br><span style="color: #9467bd;">&#8212;</span> {self.legend_text[3]} ')
        else:
            row_text_3_1 = ''
        if self.legend_text and len(self.legend_text) > 4 and self.legend_text[4] != "":
            row_text_3_2 = (f'<span style="color: #8c564b;">&#8212;</span> {self.legend_text[4]}')
        else:
            row_text_3_2 = ''
        if self.legend_text and len(self.legend_text) > 5 and self.legend_text[5] != "":
            row_text_4_1 = (f'<br><span style="color: #e377c2;">&#8212;</span> {self.legend_text[5]} ')
        else:
            row_text_4_1 = ''
        if self.legend_text and len(self.legend_text) > 6 and self.legend_text[6] != "":
            row_text_4_2 = (f'<span style="color: #7f7f7f;">&#8212;</span> {self.legend_text[6]}')
        else:
            row_text_4_2 = ''

        text = (row_text_1_1, row_text_1_2,
                row_text_2_1, row_text_2_2,
                row_text_3_1, row_text_3_2,
                row_text_4_1, row_text_4_2)
        html_content = "".join(text)
        self.text_widget.setText(html_content)
        self.text_widget.setWordWrap(True)
        self.text_widget.setStyleSheet("""
                    QLabel {
                        color: black;            /* Kolor tekstu */
                        background-color: white; /* Tło prostokąta */
                        border: 1px solid black; /* Ramka prostokąta */
                        padding: 3px;           /* Wewnętrzny margines */
                        border-radius: 5px;      /* Zaokrąglone rogi */
                    }
                """)
        if not self.text_widget in [self.ukladV.itemAt(i).widget() for i in range(self.ukladV.count())]:
            self.ukladV.addWidget(self.text_widget)

    def ill(self):
        self.ill_correct = 0
        if not hasattr(self, 'df'):
            QMessageBox.warning(self, "Error", "Data is not loaded.")
            return

        # wymagaj wybranie zakresu preferencji
        selected_preferences = [item.text() for item in self.preferencesList.selectedItems() if
                                item.text() != "no preferences"]

        for item in self.preferencesList.selectedItems():
            if item.text() != "no preferences":
                if not selected_preferences:
                    QMessageBox.warning(self, "Error", "No preferences selected.")
                    return

        df_filtered = self.df.copy()

        # filtrowanie po wszystkich kolumnach wedlug set range lower/upper
        for column, (range_type, values) in self.column_ranges.items():
            if "no preferences" in selected_preferences:
                continue  # jeśli jest 'no preferences', pomijamy filtrowanie tej kolumny
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

        # Tworzenie opisu dla legendy na podstawie preferencji i zakresów
        preferences_description = "; ".join([
            f"{pref}: {self.column_ranges[pref][1][0]}-{self.column_ranges[pref][1][1]}" if self.column_ranges[pref][
                                                                                                0] == 'numeric' else f"{pref}: {', '.join(self.column_ranges[pref][1])}"
            for pref in selected_preferences if pref in self.column_ranges
        ])
        label_text = f'ILL ({preferences_description})'
        kmf_ill.plot_survival_function(ax=ax, label=label_text)
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

        # pobieranie danych z wykresu kaplana
        self.survival_probabilities = kmf_ill.survival_function_['KM_estimate'].values
        self.time_points = kmf_ill.survival_function_.index

        last_time_km = kmf_ill.survival_function_.index[-1]

        survival_values = kmf_ill.survival_function_['KM_estimate']
        n_at_risk = kmf_ill.event_table['at_risk']
        time_intervals = range(0, int(last_time_km) + 1, 2)  # zakres co 2 lata

        line_color = ax.lines[-1].get_color()
        step = 0.02
        initial_offset_x = 0.5

        for t in time_intervals:

            closest_time = min(n_at_risk.index, key=lambda x: abs(x - t))
            patients_at_t = n_at_risk.loc[closest_time]
            survival_at_t = survival_values.loc[closest_time]

            adjusted_x = t + initial_offset_x
            adjusted_y = survival_at_t + 0.05

            while adjusted_y <= survival_at_t + step:
                adjusted_y += step

            ax.text(adjusted_x, adjusted_y,
                str(patients_at_t),
                ha='center', fontsize=8, fontweight='bold',  # Grubszy tekst
                color=line_color, alpha=0.9,  # Kolor tekstu
                verticalalignment='bottom',
                path_effects=[withStroke(linewidth=3, foreground="white")])

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

        self.legend_text.append(label_text)
        #ax.get_legend().remove() ###TO WYLACZA LEGENDE Z WYKRESU - WYSTARCZY TO USUNAC I BEDZIE LEGENDA NA WYKRESIE
        self.update_legend_widget()


        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.output_dir = os.path.join("plots", timestamp)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.canvas.figure.savefig(os.path.join(self.output_dir, f"full_plot.png"))

        self.generateReportBtn.setEnabled(True)
        self.editChartBtn.setEnabled(True)

        self.resize(self.width() + 200, self.height() + 500)
        self.center()
        self.ill_correct = 1

        return preferences_description

    def addCurve(self):
        if not hasattr(self, 'df'):
            QMessageBox.warning(self, "Error", "Data is not loaded.")
            return
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

        selected_preferences = [item.text() for item in self.preferencesList.selectedItems() if
                                item.text() != "no preferences"]

        for item in self.preferencesList.selectedItems():
            if item.text() != "no preferences":
                if not selected_preferences:
                    QMessageBox.warning(self, "Error", "No preferences selected.")
                    return

        df_filtered = self.df.copy()

        for column, (range_type, values) in self.column_ranges.items():
            if "no preferences" in selected_preferences:
                continue  # jeśli jest 'no preferences', pomijamy filtrowanie tej kolumny
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

        predefined_colors = [
            '#1f77b4',  # niebieski
            '#ff7f0e',  # pomarańczowy
            '#2ca02c',  # zielony
            '#d62728',  # czerwony
            '#9467bd',  # fioletowy
            '#8c564b',  # brązowy
            '#e377c2',  # różowy
            '#7f7f7f',  # szary
        ]

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
        label_text = f'ILL ({preferences_description})'
        kmf_additional.plot_survival_function(ax=ax, label=label_text, color=selected_color)
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
        ax.legend().remove()

        self.legend_text.append(label_text)
        self.update_legend_widget()
        last_time_km = kmf_additional.survival_function_.index[-1]

        time_intervals = range(0, int(last_time_km) + 1, 2)  # zakres co 2 lata
        survival_values = kmf_additional.survival_function_['KM_estimate']
        n_at_risk = kmf_additional.event_table['at_risk']

        self.time_points = kmf_additional.survival_function_.index.tolist()
        self.survival_probabilities = kmf_additional.survival_function_['KM_estimate'].tolist()

        global is_first_call, global_iteration_offset_y  # Użycie globalnej zmiennej
        drawn_text_positions = []
        offset_step_y = 0.2
        initial_offset_x = -0.5

        for t in time_intervals:
            closest_time = min(n_at_risk.index, key=lambda x: abs(x - t))
            patients_at_t = n_at_risk.loc[closest_time]
            survival_at_t = survival_values.loc[closest_time]

            # Specjalne przesunięcie dla timeline = 0
            adjusted_x = t + initial_offset_x  # Pozycja w osi X pozostaje bez zmian
            adjusted_y = survival_at_t - self.global_iteration_offset  # Przesunięcie w pionie dla kolejnych iteracji

                # Sprawdzenie kolizji z wcześniej dodanym tekstem
            while any(abs(adjusted_x - x) < 0.5 and abs(adjusted_y - y) < 0.05 for x, y in drawn_text_positions):
                adjusted_y += 0.02  # Standardowy krok przesunięcia w osi Y

            # Rysowanie tekstu
            ax.text(adjusted_x, adjusted_y,
                    str(patients_at_t),
                    ha='center', fontsize=8, fontweight='bold',  # Grubszy tekst
                    color=selected_color, alpha=0.9,  # Kolor tekstu
                    verticalalignment='bottom',
                    path_effects=[withStroke(linewidth=3, foreground="white")])  # Obramowanie
            drawn_text_positions.append((adjusted_x, adjusted_y))  # Dodanie nowej pozycji tekstu do listy

        self.global_iteration_offset += (offset_step_y/3)
        self.canvas.draw()

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        if not hasattr(self, 'output_dir'):
            self.output_dir = os.path.join("plots", timestamp)
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

        self.canvas.figure.savefig(os.path.join(self.output_dir, f"updated_plot_{existing_lines + 1}.png"))
        self.preferencesList.clearSelection()
        self.preferencesList.setEnabled(True)
        self.setRangeBtn.setEnabled(True)
        self.column_ranges = {}
        self.center()

        curve_id = preferences_description
        selected_tests = [item.text() for item in self.testsList.selectedItems()]
        # results_storage = TestResultsStorage()
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
            elif test == "AUC":
                self.run_AUC(curve_id)
            elif test == "Kolomorow Smirnow":
                self.run_KS_test(curve_id)
            elif test == "AUC Interpolated":
                self.run_AUC_interpolated(curve_id)
            elif test == "Kolomorow Smirnow Interpolated":
                self.run_KS_test_interpolated(curve_id)
            elif test == "Srednia roznica interpolated":
                self.run_mean_diff(curve_id)
            elif test == "Mann-Whitney U test":
                self.run_mann_whitney_u(curve_id)

    def generateReport(self):
        # Wyświetlenie dialogu do ustawień raportu
        dialog = ReportOptionsDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return

        # Pobranie opcji z dialogu
        options = dialog.getOptions()
        report_name = options["report_name"] or "report"
        save_chart_separately = options["save_chart_separately"]

        # Ścieżka do zapisu raportu
        report_path = os.path.join(self.output_dir, f"{report_name}.pdf")

        # Tworzenie raportu PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Statistical Test Report", ln=True, align='C')

        # Nagłówki i metadane
        pdf.cell(200, 10, txt=f"Report Name: {report_name}", ln=True)
        pdf.cell(200, 10, txt=f"Generated at: {self.output_dir}", ln=True)
        pdf.ln(10)

        # Wyniki testów statystycznych
        results = self.results_storage.get_all_results()
        for test, curves in results.items():
            pdf.cell(200, 10, txt=f"Test: {test}", ln=True)
            for curve_id, metrics in curves.items():
                pdf.cell(200, 10, txt=f"  Curve: {curve_id}", ln=True)
                for metric, value in metrics.items():
                    pdf.cell(200, 10, txt=f"    {metric}: {value}", ln=True)
            pdf.ln(5)

        # Dodanie wykresu do raportu PDF
        chart_image_path = os.path.join(self.output_dir, f"{report_name}_chart.png")
        self.canvas.figure.savefig(chart_image_path, bbox_inches="tight", dpi=300)
        pdf.cell(200, 10, txt=f"Chart included in report and saved as: {chart_image_path}", ln=True)
        pdf.image(chart_image_path, x=10, y=pdf.get_y() + 10, w=190)
        pdf.ln(90)  # Przesunięcie po wykresie

        # Zapisanie wykresu jako osobnego pliku, jeśli opcja została zaznaczona
        if save_chart_separately:
            pdf.cell(200, 10, txt=f"Chart also saved separately at: {chart_image_path}", ln=True)

        # Zapisanie raportu PDF
        pdf.output(report_path)

        # Informacja o zakończeniu
        self.resultEdt.setText(f"Report saved at: {report_path}")
        QMessageBox.information(self, "Report", f"Report saved at: {report_path}")

    def openEditChartWindow(self):
        if hasattr(self, 'canvas') and self.canvas is not None:
            self.editChartWindow = ChartEditorDialog(self.canvas.figure)
            self.editChartWindow.show()
        else:
            QMessageBox.warning(self, "Error", "No chart available for editing.")

    def run_AUC(self, curve_id):  # porównanie pól pod krzywymi
        time_points_ill = self.time_points
        survival_probabilities_ill = self.survival_probabilities

        time_points_gus = self.x_data_trimmed
        survival_probabilities_gus = self.y_data_probability_trimmed

        # Wyświetlenie wartości time_points_ill i survival_probabilities_ill
        # print("Time Points (ILL):", time_points_ill)
        # print("Survival Probabilities (ILL):", survival_probabilities_ill)

        # Opcjonalnie: sprawdzenie długości tablic
        # print("Length of Time Points (ILL):", len(time_points_ill))
        # print("Length of Survival Probabilities (ILL):", len(survival_probabilities_ill))

        # Wyświetlenie wartości time_points_gus i survival_probabilities_gus
        # print("Time Points (gus):", time_points_gus)
        # print("Survival Probabilities (gus):", survival_probabilities_gus)

        # Opcjonalnie: sprawdzenie długości tablic
        # print("Length of Time Points (gus):", len(time_points_gus))
        # print("Length of Survival Probabilities (gus):", len(survival_probabilities_gus))

        auc_ill = np.trapz(survival_probabilities_ill, x=time_points_ill)
        auc_gus = np.trapz(survival_probabilities_gus, x=time_points_gus)
        auc_diff = abs(auc_ill - auc_gus)

        # print(f"AUC_gus:{auc_gus}")
        # print(f"AUC_ill:{auc_ill}")
        # print(f"AUC_diff:{auc_diff}")

        # Formatowanie liczb do trzech miejsc po przecinku
        formatted_auc_ill = f"{auc_ill:.3f}"
        formatted_auc_gus = f"{auc_gus:.3f}"
        formatted_auc_diff = f"{auc_diff:.3f}"

        self.results_storage.add_result("AUC", curve_id, {"AUC_ILL": formatted_auc_ill, "AUC_GUS": formatted_auc_gus,
                                                          "AUC_DIFF": formatted_auc_diff})

        # Ustawianie tekstu z poprawnym formatowaniem
        self.resultEdt.setText(
            f"AUC test: Chorzy = {formatted_auc_ill},GUS = {formatted_auc_gus}, Roznica= {formatted_auc_diff}"
        )
        text = f"AUC test: Chorzy = {formatted_auc_ill},GUS = {formatted_auc_gus},Roznica = {formatted_auc_diff}"

        # Przesyłanie tekstu do funkcji `time`
        self.time(text)

        # Informacja w okienku dialogowym
        QMessageBox.information(self, "AUC test",
                                "Wykonano test AUC, kliknij OK aby przejść do wyniku kolejnego testu")

        all_results = self.results_storage.get_all_results()
        print("Wszystkie wyniki:", all_results)

    def run_AUC_interpolated(self, curve_id):  # porównanie pól pod krzywymi
        time_points_ill = self.time_points  # wiecej puntkow
        survival_probabilities_ill = self.survival_probabilities

        time_points_gus = self.x_data_trimmed  # mniej punktow
        survival_probabilities_gus = self.y_data_probability_trimmed

        interpolator = interp1d(time_points_gus, survival_probabilities_gus, kind='linear', fill_value="extrapolate")
        survival_probabilities_gus_interpolated = interpolator(time_points_ill)

        # Opcjonalnie: sprawdzenie długości tablic
        print("Length of Time Points (ILL):", len(time_points_ill))
        print("Length of Survival Probabilities (ILL):", len(survival_probabilities_ill))

        print("Length of Time Points (ILL):", len(time_points_gus))
        print("Length of Survival Probabilities (ILL):", len(survival_probabilities_gus))

        # print("Length of Time Points (gus_inter):", len(survival_probabilities_gus_interpolated))
        # print("Length of Survival Probabilities (gus_inter):", len(survival_probabilities_gus_interpolated))

        print("AUC - Time Points ILL:", time_points_ill)
        print("AUC - Survival Probabilities ILL:", survival_probabilities_ill)

        print("AUC - Time Points GUS (interpolated):", time_points_ill)
        print("AUC - Survival Probabilities GUS (interpolated):", survival_probabilities_gus_interpolated)

        auc_ill = np.trapz(survival_probabilities_ill, x=time_points_ill)
        auc_gus = np.trapz(survival_probabilities_gus_interpolated, x=time_points_ill)
        auc_diff = abs(auc_ill - auc_gus)

        # Formatowanie liczb do trzech miejsc po przecinku
        formatted_auc_ill = f"{auc_ill:.3f}"
        formatted_auc_gus = f"{auc_gus:.3f}"
        formatted_auc_diff = f"{auc_diff:.3f}"

        self.results_storage.add_result("AUC interpolated", curve_id,
                                        {"AUC_ILL": formatted_auc_ill, "AUC_GUS": formatted_auc_gus,
                                         "AUC_DIFF": formatted_auc_diff})

        self.resultEdt.setText(
            f"AUC test interpolated: Chorzy = {formatted_auc_ill},GUS = {formatted_auc_gus}, Roznica= {formatted_auc_diff}"
        )
        text = f"AUC test interpolated: Chorzy = {formatted_auc_ill},GUS = {formatted_auc_gus},Roznica = {formatted_auc_diff}"
        self.time(text)
        QMessageBox.information(self, "AUC test",
                                "Wykonano test AUC po interpolacji, kliknij OK aby przejsc do wyniku kolejnego testu")
        all_results = self.results_storage.get_all_results()
        print("Wszystkie wyniki:", all_results)

    def run_KS_test(self, curve_id):

        survival_probabilities_ill = self.survival_probabilities
        survival_probabilities_gus = self.y_data_probability_trimmed

        ks_stat, p_value = ks_2samp(survival_probabilities_gus, survival_probabilities_ill)

        self.results_storage.add_result("KS test", curve_id, {"KS_stat": ks_stat, "P-value": p_value})

        self.resultEdt.setText(
            f"Kolomorow Smirnow test: Statystyka KS = {ks_stat}, p-value = {p_value}")
        text = f"Kolomorow Smirnow test: Statystyka KS = {ks_stat}, p-value = {p_value}"
        self.time(text)
        QMessageBox.information(self, "Kolomorow Smirnow test",
                                "Wykonano test Kolomorow Smirnow, kliknij OK aby przejść do wyniku kolejnego testu")
        all_results = self.results_storage.get_all_results()
        print("Wszystkie wyniki:", all_results)

    def run_KS_test_interpolated(self, curve_id):

        time_points_ill = self.time_points
        time_points_gus = self.x_data_trimmed
        survival_probabilities_ill = self.survival_probabilities
        survival_probabilities_gus = self.y_data_probability_trimmed

        interpolator = interp1d(time_points_gus, survival_probabilities_gus, kind='linear', fill_value="extrapolate")
        survival_probabilities_gus_interpolated = interpolator(time_points_ill)

        ks_stat, p_value = ks_2samp(survival_probabilities_gus_interpolated, survival_probabilities_ill)

        self.results_storage.add_result("KS test", curve_id, {"KS_stat": ks_stat, "P-value": p_value})

        self.resultEdt.setText(
            f"Kolomorow Smirnow test interpolated: Statystyka KS = {ks_stat}, p-value = {p_value}")
        text = f"Kolomorow Smirnow test interpolated: Statystyka KS = {ks_stat}, p-value = {p_value}"
        self.time(text)
        QMessageBox.information(self, "Kolomorow Smirnow test interpolated",
                                "Wykonano test Kolomorow Smirnow po interpolacji, kliknij OK aby przejść do wyniku kolejnego testu")
        all_results = self.results_storage.get_all_results()
        print("Wszystkie wyniki:", all_results)

    def run_mean_diff(self, curve_id):
        time_points_ill = self.time_points  # wiecej puntkow
        survival_probabilities_ill = self.survival_probabilities

        time_points_gus = self.x_data_trimmed  # mniej punktow
        survival_probabilities_gus = self.y_data_probability_trimmed

        interpolator = interp1d(time_points_gus, survival_probabilities_gus, kind='linear', fill_value="extrapolate")
        survival_probabilities_gus_interpolated = interpolator(time_points_ill)

        diff = np.mean(np.abs(survival_probabilities_ill - survival_probabilities_gus_interpolated))

        self.results_storage.add_result("Mean diff test", curve_id, {"Mean_diff": diff})

        self.resultEdt.setText(
            f"Srednia roznica pomiedzy ppunktami wykresu: srednia roznica = {diff}")
        text = f"Srednia roznica pomiedzy ppunktami wykresu: srednia roznica = {diff}"
        self.time(text)
        QMessageBox.information(self, "Srednia roznica pomiedzy ppunktami wykresu",
                                "Obliczono srednia roznice pomiedzy ppunktami wykresu, kliknij OK aby przejść do wyniku kolejnego testu")
        all_results = self.results_storage.get_all_results()
        print("Wszystkie wyniki:", all_results)

    def run_mann_whitney_u(self, curve_id):
        time_points_ill = self.time_points  # wiecej puntkow
        survival_probabilities_ill = self.survival_probabilities
        print(f"Time_points_ill: {time_points_ill}")
        print(f"Survival_probabilities_ill: {survival_probabilities_ill}")

        time_points_gus = self.x_data_trimmed  # mniej punktow
        survival_probabilities_gus = self.y_data_probability_trimmed

        print(f"time_points_gus: {time_points_gus}")
        print(f"survival_probabilities_gus: {survival_probabilities_gus}")

        interpolator = interp1d(time_points_gus, survival_probabilities_gus, kind='linear', fill_value="extrapolate")
        survival_probabilities_gus_interpolated = interpolator(time_points_ill)
        print(f"Suv_gur_interpolated = {survival_probabilities_gus_interpolated}")

        stat, p_value = mannwhitneyu(survival_probabilities_gus_interpolated, survival_probabilities_ill,
                                     alternative='two-sided')

        self.results_storage.add_result("Mann-Whitney U", curve_id, {"Statystyka U": stat, "P-value": p_value})

        self.resultEdt.setText(
            f"Test Manna-Whitneya U: Statystyka U = {stat}, P-value = {p_value}")
        text = f"Test Manna-Whitneya U: Statystyka U = {stat}, P-value = {p_value}"
        self.time(text)
        QMessageBox.information(self, "Test Manna-Whitneya U",
                                "Wykonano Test Manna-Whitneya U, kliknij OK aby przejść do wyniku kolejnego testu")
        all_results = self.results_storage.get_all_results()
        print("Wszystkie wyniki:", all_results)

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
        text = f"Gehan-Wilcoxon test: Z-statystyka = {result.test_statistic}, p-wartość = {result.p_value}"
        self.time(text)
        QMessageBox.information(self, "Gehan-Wilcoxon test", "Wykonano test Gehan-Wilcoxon, kliknij OK aby przejść do wyniku kolejnego testu")

    #def run_cox_mantel(self):  # TODO
    #    result = "in progress"
    #    self.resultEdt.setText(f"Cox-Mantel test: Chi2 = {result}, p-wartość = {result}")
    #    QMessageBox.information(self, "Cox-Mantel test", "Wykonano test Cox-Mantel, kliknij OK aby przejść do wyniku kolejnego testu")

    #def run_f_cox(self):  # TODO
    #    result = "in progress"
    #    self.resultEdt.setText(f"F Cox test: F-statystyka = {result}, p-wartość = {result}")
    #    QMessageBox.information(self, "F Cox test", "Wykonano test F Cox, kliknij OK aby przejść do wyniku kolejnego testu")

    def run_log_rank(self):
        result = logrank_test(self.T_ill, self.x_data_trimmed, event_observed_A=self.E_ill, event_observed_B=self.y_data_probability_trimmed)
        self.resultEdt.setText(f"Log-rank test: Z-statystyka = {result.test_statistic}, p-wartość = {result.p_value}")
        text = f"Log-rank test: Z-statystyka = {result.test_statistic}, p-wartość = {result.p_value}"
        self.time(text)
        QMessageBox.information(self, "Log-rank test", "Wykonano test Log-rank, kliknij OK aby przejść do wyniku kolejnego testu")

    #def run_peto_peto_wilcoxon(self):  # TODO
    #    result = "in progress"
    #    self.resultEdt.setText(f"Peto-Peto-Wilcoxon test: Z-statystyka = {result}, p-wartość = {result}")
    #    QMessageBox.information(self, "Peto-Peto-Wilcoxon test", "Wykonano test Peto-Peto-Wilcoxon, kliknij OK aby przejść do wyniku kolejnego testu")

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
        curve_id = self.ill()
        if self.ill_correct == 1:
            self.setRangeBtn.setEnabled(False)

            self.uploadBtn.setEnabled(False)
            self.addCurveBtn.setEnabled(True)
            if hasattr(self, 'testsList') and self.testsList.isVisible():
                self.testsList.setEnabled(False)
            if hasattr(self, 'preferencesList') and self.preferencesList.isVisible():
                self.preferencesList.setEnabled(False)
            self.executeBtn.setText("Break")
            self.isExecuting = True

            self.preferencesList.clearSelection()
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
                elif test == "AUC":
                    self.run_AUC(curve_id)
                elif test == "Kolomorow Smirnow":
                    self.run_KS_test(curve_id)
                elif test == "AUC Interpolated":
                    self.run_AUC_interpolated(curve_id)
                elif test == "Kolomorow Smirnow Interpolated":
                    self.run_KS_test_interpolated(curve_id)
                elif test == "Srednia roznica interpolated":
                    self.run_mean_diff(curve_id)
                elif test == "Mann-Whitney U test":
                    self.run_mann_whitney_u(curve_id)

    def breakExecution(self):
        self.testsList.clearSelection()
        self.testsList.setEnabled(False)
        self.preferencesList.clearSelection()
        self.preferencesList.clear()
        self.preferencesList.setEnabled(False)
        self.resultEdt.clear()
        self.text_widget.close()
        self.legend_text.clear()
        self.addCurveBtn.setEnabled(False)
        self.setRangeBtn.setEnabled(False)
        self.executeBtn.setEnabled(False)
        self.uploadBtn.setEnabled(True)
        for i in reversed(range(self.ukladV.count())):
            widget = self.ukladV.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                widget.setParent(None)
                self.resize(400, 270)
                self.center()

        self.executeBtn.setText("Execute")
        self.isExecuting = False
        self.column_ranges = {}

    def toggleSetRangeBtn(self):
        if self.preferencesList.isVisible():
            self.setRangeBtn.setEnabled(True)
        else:
            self.setRangeBtn.setEnabled(False)
