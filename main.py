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