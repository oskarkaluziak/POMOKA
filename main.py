from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from pomoka import POMOKAstat

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
        common_button_style = """
                            QPushButton {
                                color: black;            /* Kolor tekstu */
                                background-color: white; /* Tło prostokąta */
                                border: 2px solid black; /* Ramka prostokąta */
                                padding: 25px;            /* Wewnętrzny margines */
                                border-radius: 10px; 
                                font-size: 14px;
                                width: 400px;
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
        self.statBtn.setStyleSheet(common_button_style)
        self.modelBtn.setStyleSheet(common_button_style)
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