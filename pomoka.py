from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QVBoxLayout, QFileDialog, QComboBox
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt

class Pomoka(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.interface()
        self.isExecuting = False

    def interface(self): # interface apki

        self.label1 = QLabel("<b>Be sure to read the detailed instructions for using the program!<b>", self)
        self.label2 = QLabel("<b>Insert patient's age:<b>", self)
        self.label3 = QLabel("<b>Results:<b>", self)

        self.filePathEdt = QLineEdit()
        self.age = QLineEdit()
        self.resultEdt = QLineEdit()
        self.resultEdt.setReadOnly(True)

        self.uploadBtn = QPushButton("&Upload data", self)
        self.testsBtn = QPushButton("&Select test", self)
        self.preferencesBtn = QPushButton("&Preferences", self)
        self.executeBtn = QPushButton("&Execute", self)
        shutdownBtn = QPushButton("&Close the POMOKA app", self)

        self.ukladV = QVBoxLayout()
        self.ukladH = QHBoxLayout()

        self.ukladV.addWidget(self.label1)
        self.ukladV.addWidget(self.label2)
        self.ukladV.addWidget(self.age)
        self.ukladV.addWidget(self.label3)
        self.ukladV.addWidget(self.resultEdt)

        self.ukladH.addWidget(self.uploadBtn)
        self.ukladH.addWidget(self.testsBtn)
        self.ukladH.addWidget(self.preferencesBtn)
        self.ukladH.addWidget(self.executeBtn)

        self.ukladV.addLayout(self.ukladH)
        self.ukladV.addWidget(shutdownBtn)

        self.setLayout(self.ukladV)

        shutdownBtn.clicked.connect(self.shutdown)
        self.uploadBtn.clicked.connect(self.uploadCSV)
        self.testsBtn.clicked.connect(self.CBtests)
        self.preferencesBtn.clicked.connect(self.CBpreferences)
        self.executeBtn.clicked.connect(self.toggleExecution)

        self.resize(400, 230)
        self.center()
        self.setWindowTitle("POMOKA")
        self.show()

    def center(self):
        # Pobranie wymiarów ekranu
        screen = QApplication.desktop().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

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
            "CSV i Excel Files (*.csv *.xlsx);;CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)",
            options=options
        )
        if fileName:
            self.filePathEdt.setText(fileName)
            self.readCSV(fileName)

    def readCSV(self, fileName): # funkcja do wczytania csv/xlsx / TODO
        try:
            if fileName.endswith('.csv'):
                df = pd.read_csv(fileName)
            elif fileName.endswith('.xlsx'):
                df = pd.read_excel(fileName)
            else:
                raise ValueError("Unsupported file format")

            # Przykładowa akcja: wyświetlenie liczby wierszy i kolumn
            QMessageBox.information(self, "Plik wczytany",
                                    f"Liczba wierszy: {df.shape[0]}\nLiczba kolumn: {df.shape[1]}")
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie można wczytać pliku: {str(e)}")
    def CBtests(self): #wybor testow / TODO Perek
        self.testsComboBox = QComboBox(self)

        self.testsComboBox.addItem("Kolmogorov-Smirnov test")
        self.testsComboBox.addItem("Repeated Measures ANOVA")
        self.testsComboBox.addItem("Log-rank test")

        self.ukladV.addWidget(self.testsComboBox)
        self.testsBtn.setEnabled(False)  # dezaktywacja przycisku po dodaniu pól

    def CBpreferences(self): # TODO
        self.preferencesComboBox = QComboBox(self)
        self.preferencesComboBox.addItem("Patients with diabetes")
        self.preferencesComboBox.addItem("Patients without diabetes")

        self.ukladV.addWidget(self.preferencesComboBox)
        self.preferencesBtn.setEnabled(False)  # dezaktywacja przycisku po dodaniu pól

    def paintEvent(self, event): # funkcja zmieniajaca tło w aplikacji + autosize
        painter = QPainter(self)
        pixmap = QPixmap("POMOKA.png")
        painter.drawPixmap(self.rect(), pixmap)

    def shutdown(self): # zamykanie aplikacji poprzez przycisk
        self.close()

    def closeEvent(self, event): # zapytanie przed zamknieciem aplikacji
        odp = QMessageBox.question(
            self, 'Komunikat',
            "Are you sure you want to close?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e): # ESC na klawiaturze - tez zamyka program
        if e.key() == Qt.Key_Escape:
            self.close()

    def gus(self): #TODO
        QMessageBox.information(self, "kiedys bedzie")
        #

    def ill(self): #TODO
        QMessageBox.information(self, "kiedys bedzie")
        #

    def charts_overlay(self): #TODO
        QMessageBox.information(self, "kiedys bedzie")
        #
    def run_kolmogorov_smirnov(self): #TODO
        #
        QMessageBox.information(self, "Test Kolmogorov-Smirnov", "Wykonano test Kolmogorov-Smirnov")

    def run_repeated_measures_anova(self): #TODO
        #
        QMessageBox.information(self, "Repeated Measures ANOVA", "Wykonano test Repeated Measures ANOVA")

    def run_log_rank_test(self): #TODO
        #
        QMessageBox.information(self, "Log-rank test", "Wykonano test Log-rank")

    def toggleExecution(self):
        if self.isExecuting:
            self.breakExecution()
        else:
            self.startExecution()

    def startExecution(self):
        if not hasattr(self, 'testsComboBox') or self.testsComboBox.currentIndex() == -1:
            QMessageBox.warning(self, "Warning", "Please select a statistical test.")
            return

        self.testsBtn.setEnabled(False)
        self.preferencesBtn.setEnabled(False)
        self.age.setEnabled(False)
        self.uploadBtn.setEnabled(False)
        if hasattr(self, 'testsComboBox') and self.testsComboBox.isVisible():
            self.testsComboBox.setEnabled(False)
        if hasattr(self, 'preferencesComboBox') and self.preferencesComboBox.isVisible():
            self.preferencesComboBox.setEnabled(False)
        self.executeBtn.setText("Break")
        self.isExecuting = True

        selected_test = self.testsComboBox.currentText()
        if selected_test == "Kolmogorov-Smirnov test":
            self.run_kolmogorov_smirnov()
        elif selected_test == "Repeated Measures ANOVA":
            self.run_repeated_measures_anova()
        elif selected_test == "Log-rank test":
            self.run_log_rank_test()

        # self.gus()
        # self.ill()
        # self.charts_overlay()

        #losowy wykres do testow
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('coś tam losowego')

        self.canvas = FigureCanvas(fig)
        self.ukladV.addWidget(self.canvas, 1, Qt.AlignBottom)
        self.resize(self.width() + 400, self.height() + 400)
        self.canvas.draw()
        self.center()

    def breakExecution(self):
        for i in reversed(range(self.ukladV.count())):
            widget = self.ukladV.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                widget.setParent(None)
                self.resize(self.width() - 400, self.height() - 400)
                self.center()

        self.executeBtn.setText("Execute")
        self.isExecuting = False
        if not hasattr(self, 'testsComboBox') and self.testsComboBox.isVisible():
            self.testsBtn.setEnabled(True)
        else:
            self.testsComboBox.setEnabled(True)
        if not hasattr(self, 'preferencesComboBox') and self.preferencesComboBox.isVisible():
            self.preferencesBtn.setEnabled(True)
        else:
            self.preferencesComboBox.setEnabled(True)
        self.age.setEnabled(True)
        self.uploadBtn.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = Pomoka()
    sys.exit(app.exec_())
