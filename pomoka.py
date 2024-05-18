from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, \
    QVBoxLayout, QFileDialog, QComboBox, QAbstractItemView, QListWidget, QInputDialog
from PyQt5.QtGui import QPixmap, QPainter, QIcon
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

    def interface(self):  # interface apki
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

        # Initially disable the preferences button
        self.preferencesBtn.setEnabled(False)

        self.resize(400, 230)
        self.center()
        self.setWindowTitle("POMOKA")
        self.setWindowIcon(QIcon('icon.png'))
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
            self.askHeaderRow(fileName)

    def askHeaderRow(self, fileName):
        row, ok = QInputDialog.getInt(self, "Header Row", "Enter the row number containing column headers:", 1, 1, 100, 1)
        if ok:
            self.readCSV(fileName, row)

    def readCSV(self, fileName, headerRow):  # funkcja do wczytania csv/xlsx / TODO
        try:
            if fileName.endswith('.csv'):
                df = pd.read_csv(fileName, header=headerRow-1)
            elif fileName.endswith('.xlsx'):
                df = pd.read_excel(fileName, header=headerRow-1)
            else:
                raise ValueError("Unsupported file format")

            self.df = df
            QMessageBox.information(self, "Plik wczytany",
                                    f"Liczba wierszy: {df.shape[0]}\nLiczba kolumn: {df.shape[1]}")

            if hasattr(self, 'preferencesList'):
                self.preferencesList.clear()
                self.preferencesList.setParent(None)
                self.preferencesList.deleteLater()
                self.adjustSize()

            self.preferencesBtn.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie można wczytać pliku: {str(e)}")

    def CBtests(self):  # wybor testow / TODO Perek
        self.testsList = QListWidget(self)
        self.testsList.setSelectionMode(QAbstractItemView.MultiSelection)

        self.testsList.addItem("Kolmogorov-Smirnov test")
        self.testsList.addItem("Repeated Measures ANOVA")
        self.testsList.addItem("Log-rank test")
        self.testsList.setFixedSize(300, 75)

        default_item = self.testsList.findItems("Log-rank test", Qt.MatchExactly)[0]
        default_index = self.testsList.indexFromItem(default_item).row()
        self.testsList.setCurrentRow(default_index)

        self.ukladV.addWidget(self.testsList)
        self.testsBtn.setEnabled(False)  # dezaktywacja przycisku po dodaniu pól

    def CBpreferences(self):  # TODO
        self.preferencesList = QListWidget(self)
        self.preferencesList.setSelectionMode(QAbstractItemView.MultiSelection)

        self.preferencesList.addItem("no preferences")  # Add "no preferences" option

        if hasattr(self, 'df'):
            columns = self.df.columns
            for column in columns:
                self.preferencesList.addItem(column)

        self.preferencesList.setFixedSize(300, 75)

        self.ukladV.addWidget(self.preferencesList)
        self.preferencesBtn.setEnabled(False)  # dezaktywacja przycisku po dodaniu pól

    def paintEvent(self, event):  # funkcja zmieniajaca tło w aplikacji + autosize
        painter = QPainter(self)
        pixmap = QPixmap("POMOKA.png")
        painter.drawPixmap(self.rect(), pixmap)

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

    def gus(self):  # TODO
        QMessageBox.information(self, "kiedys bedzie")

    def ill(self):  # TODO
        QMessageBox.information(self, "kiedys bedzie")

    def charts_overlay(self):  # TODO
        QMessageBox.information(self, "kiedys bedzie")

    def run_kolmogorov_smirnov(self):  # TODO
        QMessageBox.information(self, "Test Kolmogorov-Smirnov", "Wykonano test Kolmogorov-Smirnov")

    def run_repeated_measures_anova(self):  # TODO
        QMessageBox.information(self, "Repeated Measures ANOVA", "Wykonano test Repeated Measures ANOVA")

    def run_log_rank_test(self):  # TODO
        QMessageBox.information(self, "Log-rank test", "Wykonano test Log-rank")

    def toggleExecution(self):
        if self.isExecuting:
            self.breakExecution()
        else:
            self.startExecution()

    def startExecution(self):
        if not hasattr(self, 'testsList') or not self.testsList.selectedItems():
            QMessageBox.warning(self, "Warning", "Please select a statistical test.")
            return
        if not hasattr(self, 'preferencesList') or not self.preferencesList.selectedItems():
            QMessageBox.warning(self, "Warning", "Please select preferences or 'no preferences' when not needed.")
            return

        self.testsBtn.setEnabled(False)
        self.preferencesBtn.setEnabled(False)
        self.age.setEnabled(False)
        self.uploadBtn.setEnabled(False)
        if hasattr(self, 'testsList') and self.testsList.isVisible():
            self.testsList.setEnabled(False)
        if hasattr(self, 'preferencesList') and self.preferencesList.isVisible():
            self.preferencesList.setEnabled(False)
        self.executeBtn.setText("Break")
        self.isExecuting = True

        selected_test = self.testsList.currentItem().text()
        if selected_test == "Kolmogorov-Smirnov test":
            self.run_kolmogorov_smirnov()
        elif selected_test == "Repeated Measures ANOVA":
            self.run_repeated_measures_anova()
        elif selected_test == "Log-rank test":
            self.run_log_rank_test()

        # self.gus()
        # self.ill()
        # self.charts_overlay()

        # losowy wykres do testow
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel('Ilość lat przeżywalności')
        ax.set_ylabel('Ilość pacjentów')
        ax.set_title('pacjenci w wieku: 80')

        self.canvas = FigureCanvas(fig)
        self.ukladV.addWidget(self.canvas, 1, Qt.AlignBottom)
        self.resize(self.width() + 300, self.height() + 400)
        self.canvas.draw()
        self.center()

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
        else:
            self.preferencesBtn.setEnabled(True)
        self.age.setEnabled(True)
        self.uploadBtn.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = Pomoka()
    sys.exit(app.exec_())
