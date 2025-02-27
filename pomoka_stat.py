import os
import sys
from datetime import datetime

# PySide6 imports
from PySide6.QtWidgets import (QWidget, QComboBox, QListView, QRadioButton, QMessageBox, QHBoxLayout, QScrollArea, QFileDialog, QAbstractItemView, QListWidget, QInputDialog, QTableWidget, QTableWidgetItem, QSizePolicy)
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtCore import Qt

# Data handling and analysis
import pandas as pd
import numpy as np
import re
from scipy import stats
from scipy.interpolate import interp1d
from scipy.stats import mannwhitneyu

# Matplotlib for plotting
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patheffects import withStroke
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Lifelines for survival analysis
from lifelines import KaplanMeierFitter
from scipy.stats import ks_2samp

import seaborn as sns

# Custom imports
from plot_gus import prepare_data, save_data_to_excel, lineChartOne, lineChartRange

from fpdf import FPDF
from PIL import Image

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

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

class DataResultsStorage:
    def __init__(self):
        self.results = {}

    def add_data(self, curve_id, data):
        self.results[curve_id] = data

    def get_all_data(self):
        return self.results


from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QCheckBox, QPushButton, QLabel

class CustomDialogs:
    @staticmethod
    def showWarning(parent, title, message):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setStyleSheet(CustomDialogs._getMessageBoxStyle())
        return msg_box.exec()

    @staticmethod
    def showInformation(parent, title, message):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setStyleSheet(CustomDialogs._getMessageBoxStyle())
        return msg_box.exec()

    @staticmethod
    def showQuestion(parent, title, message):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet(CustomDialogs._getMessageBoxStyle())
        return msg_box.exec()

    @staticmethod
    def getTextInput(parent, title, label, default_text=""):
        dialog = QInputDialog(parent)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setTextValue(default_text)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setStyleSheet("""
                QInputDialog {
                    background-color: #f9fafb;
                    border: none; /* Usunięcie obramowania zewnętrznego */
                    padding: 10px;
                }
                QDialog {
                }
                QInputDialog QLabel {
                    font-family: 'Roboto';
                    font-size: 14px;
                    color: #202124;
                }
                QMessageBox QPushButton, QDialogButtonBox QPushButton {
                    color: #000000;
                    background-color: white;
                    border: 2px solid #0077B6;
                    padding: 5px 10px;
                    border-radius: 8px;
                    font-family: 'Roboto';
                    font-weight: 570;
                }
                QInputDialog QPushButton:hover {
                    background-color: #e8f0fe;
                }
                QInputDialog QPushButton:pressed {
                    background-color: #d2e3fc;
                }
                QInputDialog QLineEdit {
                    border: 2px solid #0077B6;
                    border-radius: 4px;
                    padding: 5px;
                }
            """)
        ok = dialog.exec() == QDialog.Accepted
        return dialog.textValue(), ok

    def getIntInput(parent, title, label, value=0, min_val=0, max_val=100, step=1):
        dialog = QInputDialog(parent)
        dialog.setInputMode(QInputDialog.IntInput)
        dialog.setIntRange(min_val, max_val)
        dialog.setIntStep(step)
        dialog.setIntValue(value)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: #f9fafb;
                padding: 10px;
            }
            QInputDialog QLabel {
                font-family: 'Roboto';
                font-size: 14px;
                color: #202124;
            }
            QInputDialog QPushButton {
                color: #000000;
                background-color: white;
                border: 2px solid #0077B6;
                padding: 5px 10px; /* Zmniejszenie wysokości przycisków */
                border-radius: 8px;
                font-family: 'Roboto';
            }
            QInputDialog QPushButton:hover {
                background-color: #e8f0fe;
            }
            QInputDialog QPushButton:pressed {
                background-color: #d2e3fc;
            }
            QInputDialog QLineEdit {
                border: 2px solid #0077B6;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        ok = dialog.exec() == QDialog.Accepted
        return dialog.intValue(), ok
    @staticmethod
    def getItemSelection(parent, title, label, items, current=0):
        dialog = QInputDialog(parent)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setComboBoxItems(items)
        dialog.setComboBoxEditable(False)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setStyleSheet("""
                    QInputDialog {
                        background-color: #f9fafb;
                        border: none; /* Usunięcie obramowania zewnętrznego */
                        padding: 10px;
                    }
                    QDialog {
                    }
                    QInputDialog QLabel {
                        font-family: 'Roboto';
                        font-size: 14px;
                        color: #202124;
                    }
                    QInputDialog QPushButton {
                        color: #000000;
                        background-color: white;
                        border: 2px solid #0077B6;
                        padding: 5px 10px; /* Zmniejszenie wysokości przycisków */
                        border-radius: 8px;
                        font-family: 'Roboto';
                    }
                    QInputDialog QPushButton:hover {
                        background-color: #e8f0fe;
                    }
                    QInputDialog QPushButton:pressed {
                        background-color: #d2e3fc;
                    }
                    QInputDialog QLineEdit {
                        border: 2px solid #0077B6;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QComboBox {
                        border: 2px solid #0077B6;
                        border-radius: 4px;
                        padding: 5px;
                        font-family: 'Roboto';
                        font-size: 14px;
                        color: #202124;
                    }
                    QComboBox QAbstractItemView {
                        border: 2px solid #0077B6;
                        selection-background-color: #e8f0fe;
                    }
                """)
        ok = dialog.exec() == QDialog.Accepted
        return dialog.textValue(), ok

    @staticmethod
    def getFileName(parent, title="Select File", file_filter="All Files (*.*)"):
        options = QFileDialog.Options()
        dialog = QFileDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setNameFilter(file_filter)
        dialog.setOptions(options)
        dialog.setStyleSheet("""
                QFileDialog {
                    background-color: #f9fafb;
                    padding: 10px;
                }
                QFileDialog QLabel {
                    font-family: 'Roboto';
                    font-size: 14px;
                    color: #202124;
                }
                QMessageBox QPushButton, QDialogButtonBox QPushButton {
                    color: #000000;
                    background-color: white;
                    border: 2px solid #0077B6;
                    padding: 5px 10px;
                    border-radius: 8px;
                    font-family: 'Roboto';
                    font-weight: 570;
                }
                QFileDialog QPushButton:hover {
                    background-color: #e8f0fe;
                }
                QFileDialog QPushButton:pressed {
                    background-color: #d2e3fc;
                }
            """)
        if dialog.exec() == QDialog.Accepted:
            file_name = dialog.selectedFiles()[0]
        else:
            file_name = ""
        return file_name

    @staticmethod
    @staticmethod
    def _getMessageBoxStyle():
        return """
            QMessageBox {
                background-color: #f9fafb;
                border: none;
                padding: 10px;
            }
            QDialog {
            }
            QMessageBox QLabel {
                font-size: 14px;
                font-family: 'Roboto';
                color: #202124;
            }
            QMessageBox QPushButton, QDialogButtonBox QPushButton {
                color: #000000;
                background-color: white;
                border: 2px solid #0077B6;
                padding: 5px 10px;
                border-radius: 8px;
                font-family: 'Roboto';
                font-weight: 570;
            }
            QMessageBox QPushButton:hover, QDialogButtonBox QPushButton:hover {
                background-color: #e8f0fe;
            }
            QMessageBox QPushButton:pressed, QDialogButtonBox QPushButton:pressed {
                background-color: #d2e3fc;
            }
        """


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

        self.layout.addWidget(QLabel("Select report format:"))
        self.pdf_option = QRadioButton("PDF")
        self.pdf_option.setChecked(True)  # Domyślnie PDF
        self.png_option = QRadioButton("PNG")
        self.layout.addWidget(self.pdf_option)
        self.layout.addWidget(self.png_option)

        # Buttons
        self.okButton = QPushButton("OK", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        # Button layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.okButton)
        button_layout.addWidget(self.cancelButton)
        self.layout.addLayout(button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #f9fafb;
                padding: 10px;
            }
            QLabel {
                font-family: 'Roboto';
                font-size: 14px;
                color: #202124;
            }
            QLineEdit {
                border: 2px solid #0077B6;
                border-radius: 4px;
                padding: 5px;
            }
            QCheckBox, QRadioButton {
                font-family: 'Roboto';
                font-size: 14px;
                color: #202124;
            }
            QPushButton {
                color: #000000;
                background-color: white;
                border: 2px solid #0077B6;
                padding: 5px 10px;
                border-radius: 8px;
                font-family: 'Roboto';
            }
            QPushButton:hover {
                background-color: #e8f0fe;
            }
            QPushButton:pressed {
                background-color: #d2e3fc;
            }
        """)

    def getOptions(self):
        return {
            "report_name": self.reportNameInput.text(),
            "save_chart_separately": self.saveChartCheckbox.isChecked(),
            "output_format": "pdf" if self.pdf_option.isChecked() else "png",
        }
class ChartEditorDialog(QWidget):
    def __init__(self, figure, pomoka_stat, parent=None):
        super().__init__(parent)
        self.figure = figure  # Przekazujemy obiekt wykresu
        self.original_colors = []  # Przechowuje oryginalne kolory linii
        self.original_styles = []  # Przechowuje oryginalne style linii
        self.pomoka_stat = pomoka_stat  # Przechowaj instancję POMOKAstat
        self.text_visible = True
        self.initUI()
        self.tick_step = 2

    def initUI(self):
        self.setWindowTitle("Chart Editor")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.setFixedSize(300, 800)
        self.setStyleSheet("""
                    QWidget {
                        background-color: #f9fafb;
                        font-family: 'Roboto';
                    }
                """)
        # Styl przycisków
        common_button_style = """
                    QPushButton {
                        color: #000000;
                        background-color: white;
                        border: 2px solid #0077B6;
                        padding: 7px;
                        min-width: 200px;
                        max-width: 200px;
                        height: 15px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-family: 'Roboto';
                        margin: 0px 0;
                    }
                    QPushButton:hover {
                        background-color: #e8f0fe;
                    }
                    QPushButton:pressed {
                        background-color: #d2e3fc;
                    }
                    QPushButton:disabled {
                        border-color: #e8eaed;
                        color: #9aa0a6;
                    }
                """

        # Styl pól tekstowych
        line_edit_style = """
            QLineEdit {
                color: black;            /* Kolor tekstu */
                background-color: white; /* Tło prostokąta */
                border: 1px solid #0077B6; /* Ramka prostokąta */
                padding: 7px;            /* Wewnętrzny margines */
                border-radius: 8px;      /* Zaokrąglone rogi */
                font-size: 14px
            }
        """

        # Dodanie scrollowalnego widżetu
        scroll_area_style = """
                    QScrollArea {
                        border: none;
                    }
                    QScrollBar:vertical {
                        background: #f9fafb;
                        width: 12px;
                        border: 2px solid #0077B6;
                        border-radius: 0px;
                    }
                    QScrollBar::handle:vertical {
                        background: #e8f0fe;
                        min-height: 20px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background: #d2e3fc;
                    }
                    QScrollBar::handle:vertical:pressed {
                        background: #0077B6;
                    }
                    QScrollBar::sub-line, QScrollBar::add-line {
                        background: none;
                        border: none;
                        height: 0px;
                    }
                    QScrollBar::add-page, QScrollBar::sub-page {
                        background: none;
                    }
                """
        scroll_area = QScrollArea(self)
        scroll_area.setStyleSheet(scroll_area_style)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # Sekcja czcionki osi
        font_label = QLabel("Set Axis Font Size:")
        self.font_input = QLineEdit(self)
        self.font_input.setPlaceholderText("Enter font size (e.g., 12)")
        self.font_input.setStyleSheet(line_edit_style)
        layout.addWidget(font_label)
        layout.addWidget(self.font_input)

        font_apply_btn = QPushButton("Apply Font Size", self)
        font_apply_btn.clicked.connect(self.applyFontSize)
        font_apply_btn.setStyleSheet(common_button_style)
        layout.addWidget(font_apply_btn)

        # Sekcja tytułu wykresu
        title_label = QLabel("Chart Title:")
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Enter chart title (e.g., My Chart)")
        self.title_input.setStyleSheet(line_edit_style)
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)

        self.title_checkbox = QPushButton("Toggle Chart Title", self)
        self.title_checkbox.clicked.connect(self.toggleTitle)
        self.title_checkbox.setStyleSheet(common_button_style)
        layout.addWidget(self.title_checkbox)

        # Sekcja osi Y
        y_axis_label = QLabel("Y-axis Title:")
        self.y_axis_input = QLineEdit(self)
        self.y_axis_input.setPlaceholderText("Enter Y-axis title")
        self.y_axis_input.setStyleSheet(line_edit_style)
        layout.addWidget(y_axis_label)
        layout.addWidget(self.y_axis_input)

        self.add_y_axis_btn = QPushButton("Add Y Axis Title", self)
        self.add_y_axis_btn.clicked.connect(self.addYAxis)
        self.add_y_axis_btn.setStyleSheet(common_button_style)
        layout.addWidget(self.add_y_axis_btn)

        self.remove_y_axis_btn = QPushButton("Remove Y Axis Title", self)
        self.remove_y_axis_btn.clicked.connect(self.removeYAxis)
        self.remove_y_axis_btn.setStyleSheet(common_button_style)
        layout.addWidget(self.remove_y_axis_btn)

        # Sekcja osi X
        x_axis_label = QLabel("X-axis Title:")
        self.x_axis_input = QLineEdit(self)
        self.x_axis_input.setPlaceholderText("Enter X-axis title")
        self.x_axis_input.setStyleSheet(line_edit_style)
        layout.addWidget(x_axis_label)
        layout.addWidget(self.x_axis_input)

        self.add_x_axis_btn = QPushButton("Add X Axis Title", self)
        self.add_x_axis_btn.clicked.connect(self.addXAxis)
        self.add_x_axis_btn.setStyleSheet(common_button_style)
        layout.addWidget(self.add_x_axis_btn)

        self.remove_x_axis_btn = QPushButton("Remove X Axis Title", self)
        self.remove_x_axis_btn.clicked.connect(self.removeXAxis)
        self.remove_x_axis_btn.setStyleSheet(common_button_style)
        layout.addWidget(self.remove_x_axis_btn)

        # Edytowanie skoku osi X
        x_tick_step_label = QLabel("X-axis Tick Step:")
        self.x_tick_step_input = QLineEdit(self)
        self.x_tick_step_input.setPlaceholderText("Enter tick step (e.g., 1, 0.5)")
        self.x_tick_step_input.setStyleSheet(line_edit_style)
        layout.addWidget(x_tick_step_label)
        layout.addWidget(self.x_tick_step_input)

        x_tick_step_btn = QPushButton("Apply X-axis Tick Step", self)
        x_tick_step_btn.clicked.connect(self.applyXAxisTickStep)
        x_tick_step_btn.setStyleSheet(common_button_style)
        layout.addWidget(x_tick_step_btn)

        auto_month_range_btn = QPushButton("Set Monthly Range (1/12 year)", self)
        auto_month_range_btn.clicked.connect(self.setMonthlyRange)
        auto_month_range_btn.setStyleSheet(common_button_style)
        layout.addWidget(auto_month_range_btn)

        # Zakres osi X
        x_range_label = QLabel("X-axis Range:")
        self.x_range_min_input = QLineEdit(self)
        self.x_range_min_input.setPlaceholderText("Enter min value (e.g., 5)")
        self.x_range_min_input.setStyleSheet(line_edit_style)
        self.x_range_max_input = QLineEdit(self)
        self.x_range_max_input.setPlaceholderText("Enter max value (e.g., 10)")
        self.x_range_max_input.setStyleSheet(line_edit_style)
        layout.addWidget(x_range_label)
        layout.addWidget(self.x_range_min_input)
        layout.addWidget(self.x_range_max_input)

        x_range_btn = QPushButton("Apply X-axis Range", self)
        x_range_btn.clicked.connect(self.applyXAxisRange)
        x_range_btn.setStyleSheet(common_button_style)
        layout.addWidget(x_range_btn)

        # Sekcja legendy
        legend_label = QLabel("Legend:")
        self.toggle_legend_btn = QPushButton("Toggle Legend", self)
        self.toggle_legend_btn.clicked.connect(self.toggleLegend)
        self.toggle_legend_btn.setStyleSheet(common_button_style)
        layout.addWidget(legend_label)
        layout.addWidget(self.toggle_legend_btn)

        # Widocznosc napisow
        self.toggle_text_btn = QPushButton("Toggle Patient Numbers Visibility", self)
        self.toggle_text_btn.clicked.connect(self.toggle_patients_visibility)
        self.toggle_text_btn.setToolTip("Active only in Color Mode")
        self.toggle_text_btn.setStyleSheet(common_button_style)
        layout.addWidget(self.toggle_text_btn)

        # Sekcja stylów
        style_label = QLabel("Style:")
        self.black_white_btn = QPushButton("Set Black & White Style", self)
        self.black_white_btn.clicked.connect(self.setBlackAndWhiteStyle)
        self.black_white_btn.setStyleSheet(common_button_style)
        layout.addWidget(style_label)
        layout.addWidget(self.black_white_btn)

        self.color_btn = QPushButton("Restore Original Style", self)
        self.color_btn.clicked.connect(self.restoreColorStyle)
        self.color_btn.setStyleSheet(common_button_style)
        layout.addWidget(self.color_btn)
        self.color_btn.setEnabled(False)

        # Zamknięcie okna
        # Sekcja stylów
        close_label = QLabel("")
        close_btn = QPushButton("Close Chart Editor", self)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(common_button_style)
        layout.addWidget(close_label)
        layout.addWidget(close_btn)

        scroll_area.setWidget(scroll_content)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)


    def toggle_patients_visibility(self, force_hide=False):
        """Przełącz widoczność liczb nad wykresem lub wymuś ich ukrycie."""
        if force_hide:
            self.text_visible = False
        else:
            self.text_visible = not self.text_visible

        # Usuń istniejące liczby, jeśli flaga jest False
        for ax in self.figure.axes:
            for text in ax.texts:
                text.set_visible(self.text_visible)

        self.figure.canvas.draw_idle()

        # Zaktualizuj wykres w POMOKAstat
        self.pomoka_stat.canvas.draw()
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
            CustomDialogs.showWarning(self, "Input Error", "Please enter a valid font size.")
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
        self.toggle_text_btn.setEnabled(False)
        self.color_btn.setEnabled(True)
        self.black_white_btn.setEnabled(False)
        self.original_colors = [line.get_color() for ax in self.figure.axes for line in ax.get_lines()]
        self.original_styles = [line.get_linestyle() for ax in self.figure.axes for line in ax.get_lines()]
        # Zapisz oryginalne shaded areas
        self.original_shaded_areas = []
        for ax in self.figure.axes:
            collections = [child for child in ax.get_children() if
                           isinstance(child, matplotlib.collections.PolyCollection)]
            self.original_shaded_areas.append(collections)

        line_styles = ['-', '--', '-.', ':', (0, (5, 10)), (0, (5, 1)), (0, (3, 5, 1, 5)), (0, (1, 1))]  # Różne style linii
        for ax in self.figure.axes:
            for idx, line in enumerate(ax.get_lines()):
                line.set_color("black")
                line.set_linestyle(line_styles[idx % len(line_styles)])  # Unikalny styl linii dla każdej krzywej
            ax.legend()  # Aktualizuj legendę
            # Usuń zakres min-max (shaded areas)
            for collection in self.original_shaded_areas[-1]:
                collection.remove()

        self.toggle_patients_visibility(force_hide=True)
        self.figure.canvas.draw()

    def setMonthlyRange(self):
        """Ustaw automatyczny zakres miesięczny."""
        monthly_tick_step = 1 / 12  # Skok odpowiadający miesiącowi
        for ax in self.figure.axes:
            start, end = ax.get_xlim()
            if start < 0:
                start = 0  # Ustaw zawsze początkowy punkt na 0
            ticks = [round(start + i * monthly_tick_step, 10) for i in
                     range(int((end - start) / monthly_tick_step) + 1)]
            ax.set_xticks(ticks)
        self.figure.canvas.draw()
    def applyXAxisTickStep(self):
        """Zastosuj skok osi X."""
        tick_step = self.x_tick_step_input.text()
        try:
            tick_step = float(tick_step)
            for ax in self.figure.axes:
                start, end = ax.get_xlim()
                if start < 0:
                    start = 0  # Ustaw zawsze początkowy punkt na 0
                ticks = [round(start + i * tick_step, 10) for i in range(int((end - start) / tick_step) + 1)]
                ax.set_xticks(ticks)
            self.figure.canvas.draw()
            if not self.black_white_btn.isEnabled():
                self.toggle_patients_visibility(force_hide=True)
        except ValueError:
            CustomDialogs.showWarning(self, "Input Error", "Please enter a valid tick step.")

    def applyXAxisRange(self):
        """Ustaw zakres osi X i przytnij liczby pacjentów."""
        try:
            x_min = float(self.x_range_min_input.text())
            x_max = float(self.x_range_max_input.text())
            if x_min >= x_max:
                CustomDialogs.showWarning(self, "Input Error", "Min value must be less than max value.")
                return
            for ax in self.figure.axes:
                # Ustaw zakres osi X
                ax.set_xlim(x_min, x_max)

                # Przytnij liczby pacjentów
                for text in ax.texts:
                    x, y = text.get_position()  # Pobierz pozycję tekstu
                    if x_min <= x <= x_max:
                        text.set_visible(True)  # Pokaż tekst, jeśli mieści się w zakresie
                    else:
                        text.set_visible(False)  # Ukryj tekst, jeśli jest poza zakresem
            self.reapplyXAxisTickStep()
            self.figure.canvas.draw()
            if not self.black_white_btn.isEnabled():
                self.toggle_patients_visibility(force_hide=True)
        except ValueError:
            CustomDialogs.showWarning(self, "Input Error", "Please enter valid numerical values for the range.")

    def reapplyXAxisTickStep(self):
        """Ponownie zastosuj bieżący krok osi X."""
        self.tick_step = self.x_tick_step_input.text()
        try:
            tick_step = float(self.tick_step)
            for ax in self.figure.axes:
                start, end = ax.get_xlim()
                if start < 0:
                    start = 0  # Ustaw zawsze początkowy punkt na 0
                ticks = [round(start + i * tick_step, 10) for i in range(int((end - start) / tick_step) + 1)]
                ax.set_xticks(ticks)
        except ValueError:
            return
    def restoreColorStyle(self):
        """Przywraca kolorowy styl wykresu i aktualizuje legendę."""
        self.color_btn.setEnabled(False)
        self.toggle_text_btn.setEnabled(True)
        self.black_white_btn.setEnabled(True)
        self.toggle_patients_visibility()
        if not self.original_colors or not self.original_styles:
            CustomDialogs.showWarning(self, "Error", "Original styles or colors are not stored!")
            return
        i = 0
        for ax, collections in zip(self.figure.axes, self.original_shaded_areas):
            for line in ax.get_lines():
                if i < len(self.original_colors) and i < len(self.original_styles):
                    line.set_color(self.original_colors[i])  # Przywraca oryginalny kolor
                    line.set_linestyle(self.original_styles[i])  # Przywraca oryginalny styl
                    i += 1
            ax.legend()  # Aktualizuj legendę
            for collection in collections:
                ax.add_collection(collection)
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

class NonInteractiveComboBox(QComboBox):
    def __init__(self):
        super().__init__()

        # Ustawienie widoku listy i zablokowanie interakcji
        list_view = QListView(self)
        list_view.setSelectionMode(QListView.NoSelection)  # Wyłączenie zaznaczania
        self.setView(list_view)

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
        self.data_storage = DataResultsStorage()

    def interface(self):  # interface apki
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
                    QWidget {
                        background-color: #f9fafb;
                        font-family: 'Roboto';
                    }
                """)

        self.label1 = QLabel(self)
        self.label1.setText("POMOKA")
        self.label1.setStyleSheet("""
                    color: #202124;
                    font-size: 48px;
                    font-weight: bold;
                    font-family: 'Roboto';
                    text-align: center;
                    margin-top: 10px;
                """)
        self.label1.setAlignment(Qt.AlignCenter)
        self.subtitle_label = QLabel(self)
        self.subtitle_label.setText("Your gateway to powerful analytical tools.")
        self.subtitle_label.setStyleSheet("""
                    color: #5f6368;
                    font-size: 16px;
                    font-style: italic;
                    text-align: center;
                    margin-bottom: 10px;
                """)
        self.subtitle_label.setAlignment(Qt.AlignCenter)


        self.label2 = QLabel("<b>Results:<b>", self)

        self.filePathEdt = QLineEdit()
        self.resultCmb = NonInteractiveComboBox()
        self.resultCmb.setEditable(False)  # Wyłączenie edycji ręcznej

        self.uploadBtn = QPushButton("&Upload data", self)
        self.setRangeBtn = QPushButton("&Set Range", self)
        self.executeBtn = QPushButton("&Execute", self)
        self.addCurveBtn = QPushButton("&Add next curve", self)
        self.generateReportBtn = QPushButton("&Generate Report", self)
        self.editChartBtn = QPushButton("&Edit Chart", self)

        # Styl przycisków
        common_button_style = """
            QPushButton {
                color: black;            /* Kolor tekstu */
                background-color: white; /* Tło prostokąta */
                border: 2px solid #0077B6; /* Ramka prostokąta */
                padding: 2px;            /* Wewnętrzny margines */
                border-radius: 8px;      /* Zaokrąglone rogi */
                wei
            }
            QPushButton:hover {
                background-color: #e8f0fe; /* Jaśniejsze tło po najechaniu */
            }
            QPushButton:pressed {
                background-color: #d2e3fc; /* Jeszcze ciemniejsze tło po kliknięciu */
            }
            QPushButton:disabled {
                border-color: #e8eaed;
                color: #9aa0a6;          
            }
        """
        self.uploadBtn.setStyleSheet(common_button_style)
        self.setRangeBtn.setStyleSheet(common_button_style)
        self.executeBtn.setStyleSheet(common_button_style)
        self.addCurveBtn.setStyleSheet(common_button_style)
        self.generateReportBtn.setStyleSheet(common_button_style)
        self.editChartBtn.setStyleSheet(common_button_style)

        # Układ przycisków
        self.ukladV = QVBoxLayout()
        self.ukladH = QHBoxLayout()

        self.ukladV.addWidget(self.label1)
        self.ukladV.addWidget(self.subtitle_label)

        # Sekcja dla wyników
        horizontalLayoutForLabel2AndResult = QHBoxLayout()
        horizontalLayoutForLabel2AndResult.addWidget(self.label2)
        self.resultCmb.setStyleSheet("""
            QComboBox {
                color: black;                /* Kolor tekstu */
                background-color: white;     /* Tło prostokąta */
                border: 1px solid #0077B6;   /* Ramka prostokąta */
                padding: 3px;                /* Wewnętrzny margines */
                border-radius: 8px;          /* Zaokrąglone rogi */
                min-width: 770px;       /* Minimalna szerokość */
                max-width: 770px; 
                font-family: 'Roboto';
            }
            
            QComboBox::drop-down {
                border: none;                /* Usuń ramkę przycisku rozwijania */
            }
        
            QComboBox::down-arrow {
                image: url(no_arrow.png);    /* Możesz podać ścieżkę do własnej strzałki lub usunąć */
                width: 12px;                 /* Szerokość strzałki */
                height: 12px;                /* Wysokość strzałki */
            }
        
            QComboBox QAbstractItemView {
                border: 1px solid #0077B6;   /* Ramka listy rozwijanej */
                selection-background-color: #0077B6; /* Kolor tła zaznaczonego elementu */
                selection-color: white;      /* Kolor tekstu zaznaczonego elementu */
            }
        """)
        horizontalLayoutForLabel2AndResult.addWidget(self.resultCmb)
        self.ukladV.addLayout(horizontalLayoutForLabel2AndResult)

        # Dodanie przycisków do układu
        self.ukladV.addWidget(self.uploadBtn)
        self.ukladH.addWidget(self.setRangeBtn)
        self.ukladV.addWidget(self.executeBtn)
        self.ukladH.addWidget(self.addCurveBtn)
        self.ukladV.addLayout(self.ukladH)
        self.ukladV.addWidget(self.generateReportBtn)
        self.ukladV.addWidget(self.editChartBtn)
        self.editChartBtn.hide()

        mainWidget = QWidget()
        mainWidget.setLayout(self.ukladV)

        # dodanie scrollowalnego widżetu
        scroll_area_style = """
                            QScrollArea {
                                border: none;
                            }
                            QScrollBar:vertical {
                                background: #f9fafb;
                                width: 12px;
                                border: 2px solid #0077B6;
                                border-radius: 0px;
                            }
                            QScrollBar::handle:vertical {
                                background: #e8f0fe;
                                min-height: 20px;
                            }
                            QScrollBar::handle:vertical:hover {
                                background: #d2e3fc;
                            }
                            QScrollBar::handle:vertical:pressed {
                                background: #0077B6;
                            }
                            QScrollBar::sub-line, QScrollBar::add-line {
                                background: none;
                                border: none;
                                height: 0px;
                            }
                            QScrollBar::add-page, QScrollBar::sub-page {
                                background: none;
                            }
                        """

        scrollArea = QScrollArea()
        scrollArea.setStyleSheet(scroll_area_style)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(mainWidget)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(scrollArea)


        self.setLayout(mainLayout)

        # Połączenia sygnałów z funkcjami
        self.uploadBtn.clicked.connect(self.uploadCSV)
        self.setRangeBtn.clicked.connect(self.setRanges)
        self.addCurveBtn.clicked.connect(self.addCurve)
        self.executeBtn.clicked.connect(self.toggleExecution)
        self.generateReportBtn.clicked.connect(self.generateReport)
        self.editChartBtn.clicked.connect(self.openEditChartWindow)
        self.openstatusEditChartWindow = 0

        # Ustawienia początkowe
        self.setRangeBtn.setEnabled(False)
        self.addCurveBtn.setEnabled(False)
        self.generateReportBtn.setEnabled(False)
        self.editChartBtn.setEnabled(False)
        self.executeBtn.setEnabled(False)
        self.setRangeBtn.setEnabled(False)

        self.resize(900, 500)
        self.setWindowTitle("POMOKA")
        self.setWindowIcon(QIcon('images/icon.png'))

        # pref i tests
        self.CBpreferences()
        self.CBtests()
        self.preferencesList.clear()
        self.testsList.clear()
        self.preferencesList.setEnabled(False)
        self.testsList.setEnabled(False)

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
        fileName = CustomDialogs.getFileName(self, "Select File", "All Files (*.*)")
        if fileName:
            self.filePathEdt.setText(fileName)
            self.askHeaderRow(fileName)

    def askHeaderRow(self, fileName):  # funkcja pytająca o header kolumne
        row, ok = CustomDialogs.getIntInput(self, "Header Row", "Enter the row number containing column headers:", 1, 1, 100, 1)

        if ok:
            if self.verifyHeaderRow(fileName, row):
                self.readCSV(fileName, row)
            else:
                CustomDialogs.showWarning(self, "Warning",
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
            CustomDialogs.showWarning(self, "Error", f"Unable to verify header row: {str(e)}")
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
            CustomDialogs.showInformation(self, "File loaded",
                                    f"Number of rows: {df.shape[0]}\nNumber of columns: {df.shape[1]}")

            if hasattr(self, 'preferencesList'):
                self.preferencesList.clear()
                self.preferencesList.setParent(None)
                self.preferencesList.deleteLater()
                self.toggleSetRangeBtn()
                #self.adjustSize()

            self.executeBtn.setEnabled(True)
            self.setRangeBtn.setEnabled(True)
            self.CBpreferences()
            self.CBtests()
            self.uploadBtn.hide()
            self.editChartBtn.show()
            self.center()
        except Exception as e:
            CustomDialogs.showWarning(self, "Error", f"Unable to load file: {str(e)}")

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
                        border: 2px solid #0077B6; /* Ramka prostokąta */
                        padding: 3px;           /* Wewnętrzny margines */
                        border-radius: 8px;      /* Zaokrąglone rogi */
                        min-width: 400px;       /* Minimalna szerokość */
                        max-width: 500px; 
                        min-height: 100px;      /* Minimalna wysokość */
                        max-height: 100px; 
                    }
                    QListWidget::item {
                        padding: 3px;           /* Wewnętrzny margines elementów */
                    }
                    QListWidget::item:selected {
                        background-color: lightblue; /* Tło wybranego elementu */
                        color: black;               /* Kolor tekstu wybranego elementu */
                    }
                    QListWidget:disabled {
                        background-color: white; /* Subtelne jasnoszare tło dla wyłączonego przycisku */
                        color: #9aa0a6;            /* Delikatnie wyblakły tekst */
                        border-color: #e8eaed; /* Subtelna ramka */
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
                value_range, ok = CustomDialogs.getTextInput(
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
                            CustomDialogs.showWarning(
                                self,
                                "Format Error",
                                f"Invalid range format for column '{column}'. Please enter a valid numeric range: MINIMUM-MAXIMUM."
                            )
                            continue

                        lower, upper = map(int, value_range.split('-'))

                        # Check if lower bound is less than or equal to upper bound
                        if lower > upper:
                            CustomDialogs.showWarning(
                                self,
                                "Range Error",
                                f"Invalid range: the lower bound ({lower}) cannot be greater than the upper bound ({upper})."
                            )
                            continue

                        column_values = self.df[column]

                        # Filter values in the range
                        filtered_values = column_values[(column_values >= lower) & (column_values <= upper)]

                        if filtered_values.empty:
                            CustomDialogs.showWarning(
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

                        if column.lower() in ['sex', 'plec', 'płeć', 'pŁeć', 'male', 'mezczyzna', 'mężczyzna']:
                            value = 2
                            if lower == upper:
                                value = lower
                                if value in [1, 'm', 'male']:
                                    self.selected_sex = 0  # 0=dane_mezczyzn
                                elif value in [0, 'k', 'female', 'w', 'f']:
                                    self.selected_sex = 1  # 1=dane_kobiet
                            else:
                                self.selected_sex = 2
                        if column.lower() in ['female', 'kobieta']:
                            value = 2
                            if lower == upper:
                                value = lower
                                if value in [1, 'k', 'female', 'w', 'f']:
                                    self.selected_sex = 1  # 1=dane_kobiet
                                elif value in [0, 'm', 'male']:
                                    self.selected_sex = 0  # 0=dane_mezczyzn
                            else:
                                self.selected_sex = 2

                        self.column_ranges[column] = ('numeric', (lower, upper))
                        break

                    # Check if input is a comma-separated list of values (e.g., "SVG,MVG")
                    elif ',' in value_range or value_range.strip():
                        value_list = [val.strip() for val in value_range.split(',')]

                        # Verify if all entered values exist in the column
                        if not set(value_list).issubset(set(values)):
                            CustomDialogs.showWarning(
                                self,
                                "Value Error",
                                f"Some values in '{value_range}' do not exist in column '{column}'."
                            )
                            continue

                        self.column_ranges[column] = ('categorical', value_list)
                        break

                    else:
                        CustomDialogs.showWarning(
                            self,
                            "Input Error",
                            "Please enter a valid range (e.g., 'MINIMUM-MAXIMUM' or 'value1,value2,...')."
                        )
                        continue

                except ValueError:
                    CustomDialogs.showWarning(
                        self,
                        "Input Error",
                        "Invalid input. Please enter a valid numeric range or a comma-separated list of values."
                    )

    def closeEvent(self, event):  # zapytanie przed zamknieciem aplikacji
        odp = CustomDialogs.showQuestion(
            self, 'Komunikat',
            "Are you sure you want to close?"
        )
        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):  # ESC na klawiaturze - tez zamyka program
        if e.key() == Qt.Key_Escape:
            self.close()

    def resource_path(self, relative_path):
        """
        Zwraca absolutną ścieżkę do zasobu względem lokalizacji pliku .exe lub skryptu.
        """
        # Dla aplikacji zamrożonej przez cx_Freeze
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            # Dla środowiska deweloperskiego lub niezależnego uruchomienia
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(base_path, relative_path)

    def gus(self, ax, last_time_km):  # TODO
        # dwie zmienne podawane do funkcji generujacej wykres dla jednego rocznika
        ##DEBUG
        # print("=== DEBUG: START OF FUNCTION 'gus' ===")
        # print(f"Selected sex: {self.selected_sex}")
        # print(f"Selected age: {self.selected_age}")
        # print(f"Selected age start: {self.selected_age_start}")
        # print(f"Selected age end: {self.selected_age_end}")
        # print(f"Selected option: {self.selected_option}")
        # print(f"Last time KM: {last_time_km}")
        # print("=====================================")
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

        sex = self.selected_sex

        # BACKLOG jak działa:
        # self.selected_age = wiek pacjenta
        # self.selected_age_start = wiek pacjenta dolny zakres
        # self.selected_age_end = wiek pacjenta gorny zakres
        # zakres 65-70 to wtedy start = 1952, a end = 1957, a wiec z tego powodu jest to na odwrot

        # te dwie plus sex generuje wykres dla zakresu rocznikow
        opcja = self.selected_option  # czyli czy generujemy wykres dla jednego rocznika czy zakresu, 2 to zakres
        file_path = self.resource_path("data/magicdata.xlsx")
        file_path_men = self.resource_path("data/dane_mezczyzni.xlsx")
        file_path_women = self.resource_path("data/dane_kobiety.xlsx")
        file_path_all = self.resource_path("data/dane_ogolne.xlsx")
        # print(f"koncowy_gus:{self.selected_sex}")
        if sex == 0:
            sextext = 'men'
        if sex == 1:
            sextext = 'women'
        if sex == 2:
            sextext = 'men and women'
        # tworzenie plikow jesli nie istnieja (w przyszlosci przyda sie do aktualizacji danych)
        if not os.path.exists(file_path_men) or not os.path.exists(file_path_women) or not os.path.exists(
                file_path_all):
            tab_m, tab_k = prepare_data(file_path)
            save_data_to_excel(file_path_men, file_path_women, file_path_all, tab_m, tab_k)

        if opcja == 1:
            year = (2022 - self.selected_age)
            gus_chart = lineChartOne(sex, year)
            # pobranie osi z figury wykresu z GUS
            gus_ax = gus_chart.axes[0]

            # pobranie danych z osi wykresu GUS
            self.x_data = gus_ax.lines[0].get_xdata()  # Oś X (lata)
            self.y_data = gus_ax.lines[0].get_ydata()  # Oś Y (procenty przeżycia)
            # przekształcenie procentów przeżycia na prawdopodobieństwa (0-1)
            self.y_data_probability = self.y_data / 100

            # przycinanie osi X do dlugosci kmf (tylko dla testów)
            valid_indices = self.x_data <= last_time_km
            self.x_data_trimmed = self.x_data[valid_indices]
            self.y_data_probability_trimmed = self.y_data_probability[valid_indices]

            # dodanie drugiej krzywej na ten sam wykres Kaplan-Meiera
            agetext = 2022 - year
            # print (f'{self.selected_sex}')
            # print (f'{sex}')
            ax.step(self.x_data_trimmed, self.y_data_probability_trimmed, where='post',
                    label=f'HEALTHY (age: {agetext}; sex: {sextext})',
                    linestyle='-', color='orange')

            # Ustaw widoczny zakres osi X za pomocą ChartEditorDialog
            chart_editor = ChartEditorDialog(ax.get_figure(), self)
            chart_editor.x_range_min_input.setText("-0.5")
            chart_editor.x_range_max_input.setText(str(last_time_km + 0.5))
            chart_editor.applyXAxisRange()
            self.guslegend = f'HEALTHY (age: {agetext}; sex: {sextext})'
            ax.legend()

        if opcja == 2:
            year_start = (2022 - self.selected_age_end)
            year_end = (2022 - self.selected_age_start)
            gus_chart = lineChartRange(sex, year_start, year_end)
            gus_ax = gus_chart.axes[0]

            # pobranie danych z osi wykresu GUS
            self.x_data = gus_ax.lines[0].get_xdata()  # Oś X (lata)
            self.y_data = gus_ax.lines[0].get_ydata()  # Oś Y (procenty przeżycia)
            # przekształcenie procentów przeżycia na prawdopodobieństwa (0-1)
            self.y_data_probability = self.y_data / 100

            # przycinanie osi X do dlugosci kmf (tylko dla testów)
            valid_indices = self.x_data <= last_time_km
            self.x_data_trimmed = self.x_data[valid_indices]
            self.y_data_probability_trimmed = self.y_data_probability[valid_indices]

            # dodanie drugiej krzywej na ten sam wykres Kaplan-Meiera
            agetextstart = 2022 - year_start
            agetextend = 2022 - year_end
            ax.step(self.x_data_trimmed, self.y_data_probability_trimmed, where='post',
                    label=f'HEALTHY (age: {agetextend}-{agetextstart}; sex: {sextext})',
                    linestyle='-', color='orange')

            # Ustaw widoczny zakres osi X za pomocą ChartEditorDialog
            chart_editor = ChartEditorDialog(ax.get_figure(), self)
            chart_editor.x_range_min_input.setText("-0.5")
            chart_editor.x_range_max_input.setText(str(last_time_km + 0.5))
            chart_editor.applyXAxisRange()
            self.guslegend = f'HEALTHY (age: {agetextend}-{agetextstart}; sex: {sextext})'
            ax.legend()
        curve_id="GUS"
        self.data_storage.add_data(curve_id, self.y_data_probability_trimmed)

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
                        color: #000000;            /* Kolor tekstu */
                        background-color: white; /* Tło prostokąta */
                        border: 2px solid #0077B6; /* Ramka prostokąta */
                        padding: 3px;           /* Wewnętrzny margines */
                        border-radius: 8px;      /* Zaokrąglone rogi */
                        font-family: 'Roboto';
                    }
                """)
        if not self.text_widget in [self.ukladV.itemAt(i).widget() for i in range(self.ukladV.count())]:
            self.ukladV.addWidget(self.text_widget)

    def ill(self):
        self.ill_correct = 0
        if not hasattr(self, 'df'):
            CustomDialogs.showWarning(self, "Error", "Data is not loaded.")
            return

        # wymagaj wybranie zakresu preferencji
        selected_preferences = [item.text() for item in self.preferencesList.selectedItems() if
                                item.text() != "no preferences"]

        for item in self.preferencesList.selectedItems():
            if item.text() != "no preferences":
                if not selected_preferences:
                    CustomDialogs.showWarning(self, "Error", "No preferences selected.")
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
            CustomDialogs.showWarning(self, "Error", "No data matching the selected ranges.")
            return


        # sprawdzamy, czy kolumny 'time' i 'event' istnieją
        if 'time' in df_filtered.columns:
            self.T_ill = df_filtered['time']
        else:
            # jeśli nie znajdzie 'time', prosi użytkownika o wybór kolumny
            column_names = df_filtered.columns.tolist()
            self.selected_column_time, ok = CustomDialogs.getItemSelection(self, "Select column for 'time'",
                                                       "Available columns:", column_names, 0)
            if ok and self.selected_column_time:
                self.T_ill = df_filtered[self.selected_column_time]
            else:
                CustomDialogs.showWarning(self, "Error", "No column selected for 'time'.")
                return

        if 'event' in df_filtered.columns:
            self.E_ill = df_filtered['event']
        else:
            # jeśli nie znajdzie 'event', poproś użytkownika o wybór kolumny
            column_names = df_filtered.columns.tolist()
            self.selected_column_event, ok = CustomDialogs.getItemSelection(self, "Select column for 'event'",
                                                       "Available columns:", column_names, 0)
            if ok and self.selected_column_event:
                self.E_ill = df_filtered[self.selected_column_event]
            else:
                CustomDialogs.showWarning(self, "Error", "No column selected for 'event'.")
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

            # rysowanie prostokąta jako obramowanie dla tekstu
            '''bbox_width = 0.5  # Szerokość prostokąta
            bbox_height = 0.1  # Wysokość prostokąta
            rect = plt.Rectangle(
                (adjusted_x - bbox_width / 2, adjusted_y - bbox_height / 2),  # Lewy dolny róg prostokąta
                bbox_width,  # Szerokość
                bbox_height,  # Wysokość
                linewidth=1,  # Grubość linii
                edgecolor='red',  # Kolor linii
                facecolor='none',  # Bez wypełnienia
                alpha=0.9  # Przezroczystość
            )
            ax.add_patch(rect)'''
            #

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



        # 📌 Dodanie wykresu do interfejsu
        self.canvas = FigureCanvas(fig)
        self.ukladV.addWidget(self.canvas, 1, Qt.AlignBottom)
        self.canvas.draw()
        # 📌 Etykiety kolumn (wartości osi X)
        col_labels = [str(t) for t in time_intervals]

        # 📌 Pobranie wartości liczby pacjentów na ryzyku w danym czasie
        values_row = [str(n_at_risk.loc[min(n_at_risk.index, key=lambda x: abs(x - t))]) for t in time_intervals]

        # 📌 Utworzenie tabeli (2 wiersze: Time + wartości)
        num_columns = len(col_labels) + 1  # Liczba kolumn (dodatkowa na Time/Preferences)
        table_widget = QTableWidget(2, num_columns)

        # 📌 Ustawienie nagłówków pierwszej kolumny
        table_widget.setItem(0, 0, QTableWidgetItem("Time"))
        table_widget.setItem(1, 0, QTableWidgetItem(preferences_description))

        # 📌 Ustawienie danych w tabeli
        for col, value in enumerate(values_row):
            table_widget.setItem(0, col + 1, QTableWidgetItem(col_labels[col]))  # Czas w górnym wierszu
            table_widget.setItem(1, col + 1, QTableWidgetItem(value))  # Wartości w dolnym wierszu

        # 📌 **Dostosowanie szerokości tabeli**
        table_width = self.width() - 40  # Całkowita szerokość tabeli
        table_height = 100  # Wysokość tabeli

        table_widget.setFixedSize(table_width, table_height)  # Blokowanie rozmiaru
        table_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # 📌 **Dopasowanie szerokości kolumn**
        first_column_width = 100  # Ręczne dopasowanie szerokości pierwszej kolumny
        remaining_width = table_width - first_column_width - 40  # Pozostała szerokość
        column_width = remaining_width // (num_columns - 1)  # Równy podział na pozostałe kolumny

        table_widget.setColumnWidth(0, first_column_width)  # Dopasowanie szerokości pierwszej kolumny

        for col in range(1, num_columns):
            table_widget.setColumnWidth(col, column_width)  # Pozostałe kolumny równo rozłożone

        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_widget.setShowGrid(True)

        # 📌 **Usunięcie numeracji wierszy i kolumn**
        table_widget.verticalHeader().setVisible(False)
        table_widget.horizontalHeader().setVisible(False)

        # 📌 **Utworzenie kontenera do wyśrodkowania tabeli**
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(table_widget, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(layout)

        # 📌 **Ustawienie rozmiaru kontenera**
        container.setFixedSize(table_width, table_height + 20)  # Zapewnienie, że tabela będzie widoczna w całości

        # 📌 **Dodanie tabeli do interfejsu**
        self.ukladV.addWidget(container, 0, Qt.AlignCenter)

        self.legend_text.append(label_text)
        ax.get_legend().remove() ###TO WYLACZA LEGENDE Z WYKRESU - WYSTARCZY TO USUNAC I BEDZIE LEGENDA NA WYKRESIE
        self.update_legend_widget()


        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.output_dir = os.path.join("plots", timestamp)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.generateReportBtn.setEnabled(True)
        self.editChartBtn.setEnabled(True)

        self.resize(self.width() + 200, self.height() + 500)
        self.resultCmb.setStyleSheet("""
                    QComboBox {
                        color: black;                /* Kolor tekstu */
                        background-color: white;     /* Tło prostokąta */
                        border: 1px solid #0077B6;   /* Ramka prostokąta */
                        padding: 3px;                /* Wewnętrzny margines */
                        border-radius: 8px;          /* Zaokrąglone rogi */
                        min-width: 960px;       /* Minimalna szerokość */
                        max-width: 960px; 
                        font-family: 'Roboto';
                    }

                    QComboBox::drop-down {
                        border: none;                /* Usuń ramkę przycisku rozwijania */
                    }

                    QComboBox::down-arrow {
                        image: url(no_arrow.png);    /* Możesz podać ścieżkę do własnej strzałki lub usunąć */
                        width: 12px;                 /* Szerokość strzałki */
                        height: 12px;                /* Wysokość strzałki */
                    }

                    QComboBox QAbstractItemView {
                        border: 1px solid #0077B6;   /* Ramka listy rozwijanej */
                        selection-background-color: #0077B6; /* Kolor tła zaznaczonego elementu */
                        selection-color: white;      /* Kolor tekstu zaznaczonego elementu */
                    }
                """)
        self.center()
        self.ill_correct = 1

        return preferences_description



    def addCurve(self):
        if not hasattr(self, 'df'):
            CustomDialogs.showWarning(self, "Error", "Data is not loaded.")
            return
        if not hasattr(self, 'preferencesList') or self.preferencesList is None:
            CustomDialogs.showWarning(self, "Warning", "Preferences list is missing or invalid.")
            return
            # Próbuj odczytać selectedItems() tylko, jeśli preferencesList nie zostało usunięte
        try:
            if not self.preferencesList.selectedItems():
                CustomDialogs.showWarning(self, "Warning", "Please select preferences or 'no preferences' when not needed.")
                return
        except RuntimeError:
            CustomDialogs.showWarning(self, "Warning", "Preferences list has been deleted.")
            return

        for index in range(self.preferencesList.count()):
            item = self.preferencesList.item(index)
            if item.isSelected() and item.text() != "no preferences" and item.text() not in self.column_ranges:
                CustomDialogs.showWarning(self, "Warning", f"Please set range for {item.text()} before executing.")
                return

        selected_preferences = [item.text() for item in self.preferencesList.selectedItems() if
                                item.text() != "no preferences"]

        for item in self.preferencesList.selectedItems():
            if item.text() != "no preferences":
                if not selected_preferences:
                    CustomDialogs.showWarning(self, "Error", "No preferences selected.")
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
            CustomDialogs.showWarning(self, "Error", "No data matching the selected ranges.")
            return


        if 'time' in df_filtered.columns:
            T_additional = df_filtered['time']
        else:
            if self.selected_column_time:
                T_additional = df_filtered[self.selected_column_time]
            else:
                CustomDialogs.showWarning(self, "Error", "No column selected for 'time'.")
                return

        if 'event' in df_filtered.columns:
            E_additional = df_filtered['event']
        else:
            if self.selected_column_event:
                E_additional = df_filtered[self.selected_column_event]
            else:
                CustomDialogs.showWarning(self, "Error", "No column selected for 'event'.")
                return

        kmf_additional = KaplanMeierFitter()

        if not hasattr(self, 'canvas') or self.canvas is None:
            CustomDialogs.showWarning(self, "Error", "No existing plot to add a curve.")
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
            CustomDialogs.showWarning(self, "Error", "No more unique colors available.")
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

        # Sprawdź aktualny zakres osi X i przedłuż go w razie potrzeby
        current_xlim = ax.get_xlim()
        if last_time_km > current_xlim[1]:
            ax.set_xlim(current_xlim[0], last_time_km + 0.5)  # Przedłuż zakres osi X o 0.5
            print(f"Extended X-axis range: {current_xlim[0]} to {last_time_km + 0.5}")

        time_intervals = range(0, int(last_time_km) + 1, 2)  # zakres co 2 lata
        survival_values = kmf_additional.survival_function_['KM_estimate']
        n_at_risk = kmf_additional.event_table['at_risk']

        self.time_points = kmf_additional.survival_function_.index.tolist()
        self.survival_probabilities = kmf_additional.survival_function_['KM_estimate'].tolist()

        global is_first_call, global_iteration_offset_y  # Użycie globalnej zmiennej
        drawn_text_positions = []
        offset_step_y = 0.2
        initial_offset_x = -0.3

        for t in time_intervals:
            closest_time = min(n_at_risk.index, key=lambda x: abs(x - t))
            patients_at_t = n_at_risk.loc[closest_time]
            survival_at_t = survival_values.loc[closest_time]

            # Specjalne przesunięcie dla timeline = 0
            adjusted_x = t + initial_offset_x  # Pozycja w osi X pozostaje bez zmian
            adjusted_y = survival_at_t - self.global_iteration_offset  # Przesunięcie w pionie dla kolejnych iteracji
            # Sprawdzenie kolizji z wcześniej dodanym tekstem
            while any(abs(adjusted_x - x) < 0.5 and abs(adjusted_y - y) < 0.05 for x, y in drawn_text_positions):
                adjusted_y += 0.01  # Standardowy krok przesunięcia w osi Y

            # Odbicie tekstu i prostokąta, jeśli Y jest poniżej 0.05
            if adjusted_y < 0.05:
                adjusted_y = abs(adjusted_y)
                if adjusted_y > 0.15:
                    adjusted_y -= 0.10  # Odbicie w osi Y
                adjusted_x += 0.60  # Przesunięcie w osi X

            # rysowanie prostokąta jako obramowanie dla tekstu
            '''bbox_width = 0.5  # Szerokość prostokąta
            bbox_height = 0.1  # Wysokość prostokąta
            rect = plt.Rectangle(
            (adjusted_x - bbox_width / 2, adjusted_y - bbox_height / 2),  # Lewy dolny róg prostokąta
                bbox_width,  # Szerokość
                bbox_height,  # Wysokość
                linewidth=1,  # Grubość linii
                edgecolor='red',  # Kolor linii
                facecolor='none',  # Bez wypełnienia
                alpha=0.1  # Przezroczystość
            )
            ax.add_patch(rect)'''
            #

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

        #self.canvas.figure.savefig(os.path.join(self.output_dir, f"updated_plot_{existing_lines + 1}.png"))
        self.preferencesList.clearSelection()
        self.preferencesList.setEnabled(True)
        self.setRangeBtn.setEnabled(True)
        self.column_ranges = {}
        self.center()

        curve_id = preferences_description
        self.data_storage.add_data(curve_id, self.survival_probabilities)
        data_result = self.data_storage.get_all_data()
        print("Data reult:", data_result)
        selected_tests = [item.text() for item in self.testsList.selectedItems()]
        # results_storage = TestResultsStorage()
        for test in selected_tests:
            if test == "AUC":
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

        # 📌 Wywołaj po wszystkim, ale przed komunikatem o zakończeniu

        CustomDialogs.showInformation(self, "test",
                                "Execution Completed")

    def generateReport(self):
        # 📌 **Wyświetlenie dialogu do ustawień raportu**
        dialog = ReportOptionsDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return

        # 📌 **Pobranie opcji z dialogu**
        options = dialog.getOptions()
        report_name = options["report_name"] or "report"
        save_chart_separately = options["save_chart_separately"]
        output_format = options["output_format"]

        # 📌 **Tworzenie jednego folderu na raport, wykresy i wyniki**
        output_dir = os.path.join("plots", report_name)  # Teraz wszystko w jednym folderze
        os.makedirs(output_dir, exist_ok=True)  # ✅ Tworzy folder, jeśli nie istnieje

        # 📌 **Ścieżki do plików**
        report_path = os.path.join(output_dir,
                                   f"{report_name}.{output_format}")  # Raport w folderze `plots/{report_name}`
        chart_image_path = os.path.join(output_dir, f"{report_name}_chart.png")  # Wykres w tym samym folderze
        heatmap_path = os.path.join(output_dir, f"{report_name}_heatmap.png")  # Heatmapa też

        # 📌 **Uruchomienie testów ANOVA + Tukeya**
        anova_stat, anova_p_value, tukey_matrix, heatmap_path = self.run_anova_and_tukey_heatmap(self.data_storage,
                                                                                                 heatmap_path)

        # 📌 **Zapisywanie wykresu**
        try:
            self.canvas.figure.savefig(chart_image_path, bbox_inches="tight", dpi=150)
            print(f"✅ Wykres zapisany w: {chart_image_path}")
        except Exception as e:
            print(f"❌ Błąd podczas zapisywania wykresu: {e}")
            chart_image_path = None  # 🚨 Zapobiega błędowi FileNotFoundError

        # 📌 **Tworzenie PDF**
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Statistical Test Report", ln=True, align='C')

        # 📌 **Dodanie wyników testów statystycznych (wszystkie testy, nie tylko ANOVA!)**
        pdf.cell(200, 10, txt="Wyniki testów statystycznych:", ln=True)
        pdf.ln(5)
        results = self.results_storage.get_all_results()  # Pobieramy WSZYSTKIE wyniki testów
        for test, curves in results.items():
            pdf.cell(200, 10, txt=f"Test: {test}", ln=True)
            for curve_id, metrics in curves.items():
                pdf.cell(200, 10, txt=f"  Krzywa: {curve_id}", ln=True)
                for metric, value in metrics.items():
                    pdf.cell(200, 10, txt=f"    {metric}: {value}", ln=True)
            pdf.ln(5)

        # 📌 **Dodanie wyników ANOVA**
        pdf.cell(200, 10, txt="ANOVA Results:", ln=True)
        pdf.cell(200, 10, txt=f"  ANOVA F-statistic: {anova_stat:.4f}", ln=True)
        pdf.cell(200, 10, txt=f"  ANOVA p-value: {anova_p_value:.4f}", ln=True)
        pdf.ln(10)

        # 📌 **Nie dodajemy macierzy Tukeya do PDF, zapisujemy ją osobno!**
        print(f"✅ Heatmapa zapisana osobno: {heatmap_path}")

        # 📌 **Dodanie wykresu do PDF**
        if chart_image_path and os.path.exists(chart_image_path):
            if pdf.get_y() + 100 > 270:
                pdf.add_page()
            pdf.image(chart_image_path, x=10, y=pdf.get_y() + 10, w=190)
            pdf.ln(90)
        else:
            print("❌ Wykres nie został znaleziony, pomijam dodanie do PDF.")

        # 📌 **Zapisanie raportu PDF**
        pdf.output(report_path)

        # 📌 **Informacja o zakończeniu**
        CustomDialogs.showInformation(self, "Report", f"Raport i pliki zapisane w: {output_dir}")

    def openEditChartWindow(self):
        self.openstatusEditChartWindow = 1
        if hasattr(self, 'canvas') and self.canvas is not None:
            self.editChartWindow = ChartEditorDialog(self.canvas.figure, self)
            self.editChartWindow.show()
        else:
            CustomDialogs.showWarning(self, "Error", "No chart available for editing.")

    def run_anova_and_tukey_heatmap(self, data_results_storage, heatmap_path):
        # 📌 **Pobranie danych**
        data_groups = data_results_storage.get_all_data()
        labels = list(data_groups.keys())
        values = list(data_groups.values())

        # 📌 **Wykonanie testu ANOVA**
        anova_stat, anova_p_value = stats.f_oneway(*values)
        print(f"ANOVA: Statystyka F = {anova_stat:.4f}, p-value = {anova_p_value:.4f}")

        if anova_p_value >= 0.05:
            print("Brak istotnych różnic między grupami.")
            return anova_stat, anova_p_value, None, None  # ✅ Jeśli brak różnic, zwracamy None

        # 📌 **Wykonanie testu Tukeya**
        print("ANOVA wykazała istotne różnice – uruchamiam test Tukeya HSD...")
        data = []
        group_labels = []
        for label, values in data_groups.items():
            data.extend(values)
            group_labels.extend([label] * len(values))

        tukey = pairwise_tukeyhsd(np.array(data), np.array(group_labels), alpha=0.05)

        print("Tabela wyników Tukeya:")
        for result in tukey.summary().data:
            print(result)  # Wyświetla każdą linię wyników

        # 📌 **Tworzenie macierzy Tukeya**
        tukey_matrix = pd.DataFrame(index=labels, columns=labels, dtype=float)
        for result in tukey.summary().data[1:]:
            g1, g2, _, p, _, *_ = result
            tukey_matrix.loc[g1, g2] = p
            tukey_matrix.loc[g2, g1] = p  # Teraz obie połowy są wypełnione

        # 📌 **Zapisywanie heatmapy**
        try:
            plt.figure(figsize=(8, 6))
            sns.heatmap(tukey_matrix, annot=True, cmap="coolwarm", center=0.05, linewidths=0.5, vmin=0, vmax=1)
            plt.title("Macierz testu Tukeya (p-value)")
            plt.savefig(heatmap_path, bbox_inches="tight", dpi=150)
            plt.close()
            print(f"✅ Heatmapa zapisana w: {heatmap_path}")
        except Exception as e:
            print(f"❌ Błąd podczas zapisywania heatmapy: {e}")
            heatmap_path = None

        return anova_stat, anova_p_value, tukey_matrix, heatmap_path

        try:
            plt.figure(figsize=(8, 6))
            sns.heatmap(tukey_matrix, annot=True, cmap="coolwarm", center=0.05, linewidths=0.5, vmin=0, vmax=1)
            plt.title("Macierz testu Tukeya (p-value)")
            plt.savefig(heatmap_path, bbox_inches="tight", dpi=150)
            plt.close()
            print(f"✅ Heatmapa zapisana w: {heatmap_path}")
        except Exception as e:
            print(f"❌ Błąd podczas zapisywania heatmapy: {e}")
            heatmap_path = None  # 🚨 Unikamy błędu FileNotFoundError

        return anova_stat, anova_p_value, tukey_matrix, heatmap_path  # ✅ Teraz zawsze zwracamy poprawną ścieżkę

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
        self.resultCmb.addItem(f"AUC test: Chorzy = {formatted_auc_ill},GUS = {formatted_auc_gus}, Roznica= {formatted_auc_diff}")


        # Informacja w okienku dialogowym

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
        #print("Length of Time Points (ILL):", len(time_points_ill))
        #print("Length of Survival Probabilities (ILL):", len(survival_probabilities_ill))

        #print("Length of Time Points (ILL):", len(time_points_gus))
        #print("Length of Survival Probabilities (ILL):", len(survival_probabilities_gus))

        # print("Length of Time Points (gus_inter):", len(survival_probabilities_gus_interpolated))
        # print("Length of Survival Probabilities (gus_inter):", len(survival_probabilities_gus_interpolated))

        #print("AUC - Time Points ILL:", time_points_ill)
        #print("AUC - Survival Probabilities ILL:", survival_probabilities_ill)

        #print("AUC - Time Points GUS (interpolated):", time_points_ill)
        #print("AUC - Survival Probabilities GUS (interpolated):", survival_probabilities_gus_interpolated)

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


        self.resultCmb.addItem(f"AUC test interpolated: Chorzy = {formatted_auc_ill},GUS = {formatted_auc_gus}, Roznica= {formatted_auc_diff}"
        )
        all_results = self.results_storage.get_all_results()
        #print("Wszystkie wyniki:", all_results)

    def run_KS_test(self, curve_id):

        survival_probabilities_ill = self.survival_probabilities
        survival_probabilities_gus = self.y_data_probability_trimmed

        ks_stat, p_value = ks_2samp(survival_probabilities_gus, survival_probabilities_ill)

        self.results_storage.add_result("KS test", curve_id, {"KS_stat": ks_stat, "P-value": p_value})

        self.resultCmb.addItem(f"Kolomorow Smirnow test: Statystyka KS = {ks_stat}, p-value = {p_value}")

        all_results = self.results_storage.get_all_results()
        #print("Wszystkie wyniki:", all_results)

    def run_KS_test_interpolated(self, curve_id):

        time_points_ill = self.time_points
        time_points_gus = self.x_data_trimmed
        survival_probabilities_ill = self.survival_probabilities
        survival_probabilities_gus = self.y_data_probability_trimmed

        interpolator = interp1d(time_points_gus, survival_probabilities_gus, kind='linear', fill_value="extrapolate")
        survival_probabilities_gus_interpolated = interpolator(time_points_ill)

        ks_stat, p_value = ks_2samp(survival_probabilities_gus_interpolated, survival_probabilities_ill)

        self.results_storage.add_result("KS test interpolated", curve_id, {"KS_stat": ks_stat, "P-value": p_value})

        self.resultCmb.addItem(f"Kolomorow Smirnow test interpolated: Statystyka KS = {ks_stat}, p-value = {p_value}")

        all_results = self.results_storage.get_all_results()
        #print("Wszystkie wyniki:", all_results)

    def run_mean_diff(self, curve_id):
        time_points_ill = self.time_points  # wiecej puntkow
        survival_probabilities_ill = self.survival_probabilities

        time_points_gus = self.x_data_trimmed  # mniej punktow
        survival_probabilities_gus = self.y_data_probability_trimmed

        interpolator = interp1d(time_points_gus, survival_probabilities_gus, kind='linear', fill_value="extrapolate")
        survival_probabilities_gus_interpolated = interpolator(time_points_ill)

        diff = np.mean(np.abs(survival_probabilities_ill - survival_probabilities_gus_interpolated))
        print("ID:", curve_id, "diff:", diff)
        # Dodanie wyniku dla każdej krzywej

        self.results_storage.add_result("Mean diff test", curve_id, {"Mean_diff": diff})

        self.resultCmb.addItem(f"Srednia roznica pomiedzy punktami wykresu: srednia roznica = {diff}")


        all_results = self.results_storage.get_all_results()
        print("Wszystkie wyniki:", all_results)

    def run_mann_whitney_u(self, curve_id):
        time_points_ill = self.time_points  # wiecej puntkow
        survival_probabilities_ill = self.survival_probabilities
        #print(f"Time_points_ill: {time_points_ill}")
        #print(f"Survival_probabilities_ill: {survival_probabilities_ill}")

        time_points_gus = self.x_data_trimmed  # mniej punktow
        survival_probabilities_gus = self.y_data_probability_trimmed

        #print(f"time_points_gus: {time_points_gus}")
        #print(f"survival_probabilities_gus: {survival_probabilities_gus}")

        interpolator = interp1d(time_points_gus, survival_probabilities_gus, kind='linear', fill_value="extrapolate")
        survival_probabilities_gus_interpolated = interpolator(time_points_ill)
        #print(f"Suv_gur_interpolated = {survival_probabilities_gus_interpolated}")

        stat, p_value = mannwhitneyu(survival_probabilities_gus_interpolated, survival_probabilities_ill,
                                     alternative='two-sided')

        self.results_storage.add_result("Mann-Whitney U", curve_id, {"Statystyka U": stat, "P-value": p_value})

        self.resultCmb.addItem(
            f"Test Manna-Whitneya U: Statystyka U = {stat}, P-value = {p_value}")

        all_results = self.results_storage.get_all_results()
        #print("Wszystkie wyniki:", all_results)

    def toggleExecution(self):
        if self.isExecuting:
            self.breakExecution()
        else:
            self.startExecution()

    def startExecution(self):
        if not hasattr(self, 'testsList') or self.testsList is None or not self.testsList.selectedItems():
            CustomDialogs.showWarning(self, "Warning", "Please select a statistical test.")
            return

            # Sprawdź, czy preferencesList istnieje i jest poprawnym widgetem
        if not hasattr(self, 'preferencesList') or self.preferencesList is None:
            CustomDialogs.showWarning(self, "Warning", "Preferences list is missing or invalid.")
            return

            # Próbuj odczytać selectedItems() tylko, jeśli preferencesList nie zostało usunięte
        try:
            if not self.preferencesList.selectedItems():
                CustomDialogs.showWarning(self, "Warning", "Please select preferences or 'no preferences' when not needed.")
                return
        except RuntimeError:
            CustomDialogs.showWarning(self, "Warning", "Preferences list has been deleted.")
            return

        for index in range(self.preferencesList.count()):
            item = self.preferencesList.item(index)
            if item.isSelected() and item.text() != "no preferences" and item.text() not in self.column_ranges:
                CustomDialogs.showWarning(self, "Warning", f"Please set range for {item.text()} before executing.")
                return
        curve_id = self.ill()
        if self.ill_correct == 1:
            self.setRangeBtn.setEnabled(False)

            self.uploadBtn.hide()
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

            self.data_storage.add_data(curve_id, self.survival_probabilities)
            data_result = self.data_storage.get_all_data()
            print("wyniki data:", data_result)
            selected_tests = [item.text() for item in self.testsList.selectedItems()]
            for test in selected_tests:
                if test == "AUC":
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
            CustomDialogs.showInformation(self, "test",
                                    "Execution Completed")

    def breakExecution(self):
        self.testsList.clearSelection()
        self.testsList.setEnabled(False)
        self.preferencesList.clearSelection()
        self.preferencesList.clear()
        self.preferencesList.setEnabled(False)
        self.resultCmb.clear()
        self.text_widget.close()
        self.legend_text.clear()
        self.addCurveBtn.setEnabled(False)
        self.setRangeBtn.setEnabled(False)
        self.executeBtn.setEnabled(False)
        self.generateReportBtn.setEnabled(False)
        self.editChartBtn.hide()
        self.testsList.clear()
        self.uploadBtn.show()
        if self.openstatusEditChartWindow == 1:
            self.editChartWindow.hide()
        for i in reversed(range(self.ukladV.count())):
            widget = self.ukladV.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                widget.setParent(None)
                self.resize(900, 500)
                self.resultCmb.setStyleSheet("""
                            QComboBox {
                                color: black;                /* Kolor tekstu */
                                background-color: white;     /* Tło prostokąta */
                                border: 1px solid #0077B6;   /* Ramka prostokąta */
                                padding: 3px;                /* Wewnętrzny margines */
                                border-radius: 8px;          /* Zaokrąglone rogi */
                                min-width: 770px;       /* Minimalna szerokość */
                                max-width: 770px; 
                                font-family: 'Roboto';
                            }

                            QComboBox::drop-down {
                                border: none;                /* Usuń ramkę przycisku rozwijania */
                            }

                            QComboBox::down-arrow {
                                image: url(no_arrow.png);    /* Możesz podać ścieżkę do własnej strzałki lub usunąć */
                                width: 12px;                 /* Szerokość strzałki */
                                height: 12px;                /* Wysokość strzałki */
                            }

                            QComboBox QAbstractItemView {
                                border: 1px solid #0077B6;   /* Ramka listy rozwijanej */
                                selection-background-color: #0077B6; /* Kolor tła zaznaczonego elementu */
                                selection-color: white;      /* Kolor tekstu zaznaczonego elementu */
                            }
                        """)
                self.center()

        self.executeBtn.setText("Execute")
        self.isExecuting = False
        self.column_ranges = {}

    def toggleSetRangeBtn(self):
        if self.preferencesList.isVisible():
            self.setRangeBtn.setEnabled(True)
        else:
            self.setRangeBtn.setEnabled(False)
