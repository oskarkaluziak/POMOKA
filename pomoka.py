from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QVBoxLayout, QFileDialog, QComboBox
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import sys
import random
import numpy as np
import matplotlib.pyplot as plt

class Pomoka(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.interface()

    def interface(self): # interface apki

        self.label1 = QLabel("<b>Be sure to read the detailed instructions for using the program!<b>", self)
        self.label2 = QLabel("", self)
        self.label3 = QLabel("<b>Insert patient's age:<b>", self)
        self.label4 = QLabel("<b>Results:<b>", self)

        self.filePathEdt = QLineEdit()
        self.age = QLineEdit()
        self.resultEdt = QLineEdit()
        self.resultEdt.setReadOnly(True)

        uploadBtn = QPushButton("&Upload data", self)
        self.testsBtn = QPushButton("&Select test", self)
        self.preferencesBtn = QPushButton("&Preferences", self)
        executeBtn = QPushButton("&Execute", self)
        shutdownBtn = QPushButton("&Close the POMOKA app", self)

        self.ukladV = QVBoxLayout()
        self.ukladH = QHBoxLayout()

        self.ukladV.addWidget(self.label1)
        self.ukladV.addWidget(self.label2)
        self.ukladV.addWidget(self.label3)
        self.ukladV.addWidget(self.age)
        self.ukladV.addWidget(self.label4)
        self.ukladV.addWidget(self.resultEdt)

        self.ukladH.addWidget(uploadBtn)
        self.ukladH.addWidget(self.testsBtn)
        self.ukladH.addWidget(self.preferencesBtn)
        self.ukladH.addWidget(executeBtn)

        self.ukladV.addLayout(self.ukladH)
        self.ukladV.addWidget(shutdownBtn)

        self.setLayout(self.ukladV)

        shutdownBtn.clicked.connect(self.shutdown)
        uploadBtn.clicked.connect(self.uploadCSV)
        self.testsBtn.clicked.connect(self.CBtests)
        self.preferencesBtn.clicked.connect(self.CBpreferences)
        executeBtn.clicked.connect(self.algorithm)

        self.setGeometry(20, 20, 400, 200)
        self.setWindowTitle("POMOKA")
        self.show()

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
        self.testsComboBox = QComboBox(self)
        self.testsComboBox.addItem("Patients with diabetes")
        self.testsComboBox.addItem("Patients without diabetes")

        self.ukladV.addWidget(self.testsComboBox)
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

    def algorithm(self):  # algorytm do robienia krzywych z danych chorych TODO

        #usuwa poprzedni wykres o ile jakiś wyświetla apka
        for i in reversed(range(self.ukladV.count())):
            widget = self.ukladV.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                widget.setParent(None)
                self.resize(self.width(), self.height() - 400)

        if not hasattr(self, 'testsComboBox') or self.testsComboBox.currentIndex() == -1:
            QMessageBox.warning(self, "Warning", "Please select a statistical test.")
            return
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

        # to losowy wykres
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('coś tam losowego')

        # to musi zostać
        self.canvas = FigureCanvas(fig)
        self.ukladV.addWidget(self.canvas, 1, Qt.AlignBottom)
        self.resize(self.width(), self.height() + 400)
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = Pomoka()
    sys.exit(app.exec_())
