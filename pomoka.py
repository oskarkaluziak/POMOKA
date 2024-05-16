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
        self.interfejs()

    def interfejs(self): # interfejs apki
        # Labely
        self.label1 = QLabel("<b>Przeczytaj koniecznie dokładną instrukcję używania programu!<b>", self)
        self.label2 = QLabel("<b>Wiek pacjenta:<b>", self)
        self.label3 = QLabel("<b>Wynik testu:<b>", self)

        # 1-liniowe pola edycyjne
        self.filePathEdt = QLineEdit()  # Pole do wyświetlania ścieżki pliku
        self.wiek = QLineEdit()
        self.wynikEdt = QLineEdit()

        self.wynikEdt.setReadOnly(True)
        self.wynikEdt.setToolTip('Wpisz <b>liczby</b> i wybierz działanie...')

        # Przyciski
        wgrajBtn = QPushButton("&Wgraj", self)
        self.testBtn = QPushButton("&Wybierz test", self)
        self.preferencjeBtn = QPushButton("&Wybierz preferencje", self)
        wykonajBtn = QPushButton("Wykonaj test", self)
        koniecBtn = QPushButton("&Zamknij aplikację POMOKA", self)

        # Układy
        self.ukladV = QVBoxLayout()
        self.ukladH = QHBoxLayout()

        # Dodanie elementów do układów
        self.ukladV.addWidget(self.label1)
        self.ukladV.addWidget(self.label2)
        self.ukladV.addWidget(self.wiek)
        self.ukladV.addWidget(self.label3)
        self.ukladV.addWidget(self.wynikEdt)

        self.ukladH.addWidget(wgrajBtn)
        self.ukladH.addWidget(self.testBtn)
        self.ukladH.addWidget(self.preferencjeBtn)
        self.ukladH.addWidget(wykonajBtn)

        self.ukladV.addLayout(self.ukladH)
        self.ukladV.addWidget(koniecBtn)

        # Ustawienie układu
        self.setLayout(self.ukladV)

        koniecBtn.clicked.connect(self.koniec)
        wgrajBtn.clicked.connect(self.wgrajPlik)
        self.testBtn.clicked.connect(self.pokazOpcjeTestow)
        self.preferencjeBtn.clicked.connect(self.pokazpreferencje)
        wykonajBtn.clicked.connect(self.dzialanie)

        self.setGeometry(20, 20, 400, 200)
        self.setWindowTitle("POMOKA")
        self.show()

    def wgrajPlik(self):  # funkcja do opcji z wgraniem pliku
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Wybierz plik CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.filePathEdt.setText(fileName)
            self.wczytajPlikCSV(fileName)

    def wczytajPlikCSV(self, fileName): # funkcja do wczytania csv / TODO
        try:
            df = pd.read_csv(fileName)
            # Przykładowa akcja: wyświetlenie liczby wierszy i kolumn
            QMessageBox.information(self, "Plik CSV wczytany", f"Liczba wierszy: {df.shape[0]}\nLiczba kolumn: {df.shape[1]}")
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie można wczytać pliku CSV: {str(e)}")

    def pokazOpcjeTestow(self): #wybor testow / TODO Perek
        self.testComboBox = QComboBox(self)

        self.testComboBox.addItem("Kolmogorov-Smirnov test")
        self.testComboBox.addItem("Repeated Measures ANOVA")
        self.testComboBox.addItem("Log-rank test")

        self.ukladV.addWidget(self.testComboBox)
        self.testBtn.setEnabled(False)  # dezaktywacja przycisku po dodaniu pól

    def pokazpreferencje(self): # TODO
        self.testComboBox = QComboBox(self)
        self.testComboBox.addItem("Pacjenci chorzy na cukrzyce")
        self.testComboBox.addItem("Pacjenci bez cukrzycy")

        self.ukladV.addWidget(self.testComboBox)
        self.preferencjeBtn.setEnabled(False)  # dezaktywacja przycisku po dodaniu pól

    def paintEvent(self, event): # funkcja zmieniajaca tło w aplikacji + autosize
        painter = QPainter(self)
        pixmap = QPixmap("zdjecie_cw.jpeg")
        painter.drawPixmap(self.rect(), pixmap)

    def koniec(self): # zamykanie aplikacji poprzez przycisk
        self.close()

    def closeEvent(self, event): # zapytanie przed zamknieciem aplikacji
        odp = QMessageBox.question(
            self, 'Komunikat',
            "Czy na pewno chcesz zamknąć?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e): # ESC na klawiaturze - tez zamyka program
        if e.key() == Qt.Key_Escape:
            self.close()
    def dzialanie(self):  # algorytm do robienia krzywych z danych chorych TODO mikolaj
        #QMessageBox.information(self, "Akcja", "Tutaj dodaj kod do wykonywania krzywej dla chorych")
        for i in reversed(range(self.ukladV.count())):
            widget = self.ukladV.itemAt(i).widget()
            if widget is not None:
                self.ukladV.removeWidget(widget)
                widget.deleteLater()

            # Tworzenie losowych danych
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        # Tworzenie wykresu
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Losowy wykres')

        # Osadzanie wykresu w aplikacji
        self.canvas = FigureCanvas(fig)

        # Utwórz pusty widget, który będzie zajmował miejsce na dnie okna
        bottom_widget = QWidget(self)
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.addWidget(self.canvas)
        self.ukladV.addWidget(bottom_widget, 1, Qt.AlignBottom)  # Rozszerzanie do pełnej szerokości, wyrównanie na dole

        # Aktualizacja widoku
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = Pomoka()
    sys.exit(app.exec_())
