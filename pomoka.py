from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
from PySide6.QtGui import QIcon, QPalette, QColor
from PySide6.QtCore import Qt
from pomoka_stat import POMOKAstat
from pomoka_model import POMOKAmodel

class POMOKAstartup(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("POMOKA menu")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#ECECED"))  # Używamy QPalette.Window zamiast QPalette.Background
        self.setPalette(palette)

        self.resize(700, 270)

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
                                width: 600px;
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

        self.statBtn.clicked.connect(self.openStatApp)
        self.modelBtn.clicked.connect(self.openModelApp)

        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignTop)
        layout.addStretch()
        layout.addWidget(self.statBtn, alignment=Qt.AlignCenter)
        layout.addWidget(self.modelBtn, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def openStatApp(self):
        self.StatApp = POMOKAstat()
        self.StatApp.show()
        self.close()

    def openModelApp(self):
        reply = QMessageBox.question(
            self,
            "Open Model App",
            "Are you sure you want to open the model application? This version is in progress.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.ModelApp = POMOKAmodel()
            self.ModelApp.show()
            self.close()

if __name__ == "__main__":
    app = QApplication([])
    startup = POMOKAstartup()
    startup.show()
    app.exec()
