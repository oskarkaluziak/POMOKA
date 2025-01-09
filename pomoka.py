from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox, QTextEdit
from PySide6.QtGui import QIcon, QColor, QFont, QPixmap
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QDesktopServices, QGuiApplication
from pomoka_stat import POMOKAstat
from pomoka_model import POMOKAmodel

class POMOKAstartup(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("POMOKA")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.setFixedSize(900, 500)

        # Set gradient background
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Lato';
            }
        """)

        # Header Container with Stylish Font
        self.header_label = QLabel(self)
        self.header_label.setText("POMOKA")
        self.header_label.setStyleSheet("""
            color: #202124;
            font-size: 48px;
            font-weight: bold;
            font-family: 'Lato';
            text-align: center;
            margin-top: 40px;
        """)
        self.header_label.setAlignment(Qt.AlignCenter)

        # Header Subtitle
        self.subtitle_label = QLabel(self)
        self.subtitle_label.setText("Your gateway to powerful analytical tools.")
        self.subtitle_label.setStyleSheet("""
            color: #5f6368;
            font-size: 16px;
            font-style: italic;
            text-align: center;
            margin-bottom: 20px;
        """)
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        # Decorative Image (Logo)
        self.image_label = QLabel(self)
        pixmap = QPixmap('images/logo.png')  # Replace with your transparent logo
        if not pixmap.isNull():
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)
        else:
            self.image_label.hide()  # Hide the label if no logo is found

        # Buttons
        self.statBtn = QPushButton("OPEN STAT APP", self)
        self.statBtn.setCursor(Qt.PointingHandCursor)

        self.modelBtn = QPushButton("OPEN MODEL APP", self)
        self.modelBtn.setCursor(Qt.PointingHandCursor)
        self.modelBtn.setEnabled(False)  # Disabled for now
        self.modelBtn.hide()

        self.reportBtn = QPushButton("GIVE YOUR FEEDBACK", self)
        self.reportBtn.setCursor(Qt.PointingHandCursor)

        self.instructionsBtn = QPushButton("INSTRUCTION", self)
        self.instructionsBtn.setCursor(Qt.PointingHandCursor)

        # Button style customization
        button_style = """
                    QPushButton {
                        color: #000000;
                        background-color: white;
                        border: 2px solid #0077B6;
                        padding: 13px;
                        min-width: 400px;
                        max-width: 400px;
                        height: 25px;
                        border-radius: 8px;
                        font-size: 16px;
                        font-family: 'Lato';
                        font-weight: 570;
                        margin: 10px 0;
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

        self.statBtn.setStyleSheet(button_style)
        self.modelBtn.setStyleSheet(button_style.replace("#4285f4", "#5f6368"))
        self.reportBtn.setStyleSheet(button_style)
        self.instructionsBtn.setStyleSheet(button_style)

        # Button Actions
        self.statBtn.setToolTip("Launch POMOKA")
        self.modelBtn.setToolTip("This feature is under development")
        self.reportBtn.setToolTip("Report an issue to administrator")
        self.instructionsBtn.setToolTip("View instruction for using POMOKA")

        self.statBtn.clicked.connect(self.openStatApp)
        self.modelBtn.clicked.connect(self.openModelApp)
        self.reportBtn.clicked.connect(self.reportToAdmin)
        self.instructionsBtn.clicked.connect(self.openInstructions)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.header_label, alignment=Qt.AlignTop)
        layout.addWidget(self.subtitle_label, alignment=Qt.AlignTop)
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.statBtn, alignment=Qt.AlignCenter)
        layout.addWidget(self.modelBtn, alignment=Qt.AlignCenter)
        layout.addWidget(self.instructionsBtn, alignment=Qt.AlignCenter)
        layout.addWidget(self.reportBtn, alignment=Qt.AlignCenter)
        layout.addStretch()

        # Footer
        self.footer_label = QLabel(self)
        self.footer_label.setText("Version 1.0 | © 2025 POMOKA")
        self.footer_label.setStyleSheet("""
            color: #5f6368;
            font-size: 12px;
            font-family: 'Lato';
            text-align: center;
            margin: 0px 0;
        """)
        layout.addWidget(self.footer_label, alignment=Qt.AlignBottom)
        self.setLayout(layout)
        self.center()
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
    def addShadowEffect(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 50))
        widget.setGraphicsEffect(shadow)

    def openStatApp(self):
        self.StatApp = POMOKAstat()
        self.StatApp.show()
        #self.close()

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

    def updateShadowColor(self):
        # Ustaw nowy kolor dla cienia
        self.shadow.setColor(self.colors[self.current_color_index])
        self.current_color_index = (self.current_color_index + 1) % len(self.colors)  # Przejdź do następnego koloru

    def reportToAdmin(self):
        QDesktopServices.openUrl(QUrl("mailto:oskar@kaluziak.pl"))

    def openInstructions(self):
        if not hasattr(self, 'instructions_window') or not self.instructions_window:
            self.instructions_window = InstructionsWindow()
        if not self.instructions_window.isVisible():
            self.instructions_window.show()
        else:
            self.instructions_window.raise_()
            self.instructions_window.activateWindow()
        self.center()

class InstructionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instruction")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.setFixedSize(600, 400)
        self.instructions_text = QTextEdit()

        # Styl okna
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Lato';
                color: #202124;
            }

            QTextEdit {
                background-color: white;
                border: 2px solid #0077B6;
                border-radius: 8px;
                padding: 10px;
                color: #202124;
                font-size: 14px;
                font-family: 'Lato';
                min-width: 536px;       /* Minimalna szerokość */
                max-width: 536px; 
                min-height: 300px;      /* Minimalna wysokość */
                max-height: 300px; 
            }

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
        """)

        button_style = """
                            QPushButton {
                                color: #000000;
                                background-color: white;
                                border: 2px solid #0077B6;
                                padding: 3px;
                                min-width: 30px;
                                max-width: 30px;
                                height: 15px;
                                border-radius: 8px;
                                font-family: 'Lato';
                                font-weight: 570;
                                margin: 5px 0;
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

        # Ustawienie layoutu
        layout = QVBoxLayout()
        self.languageBtn = QPushButton("PL", self)
        self.languageBtn.setStyleSheet(button_style)
        self.languageBtn.setToolTip("Change language")
        self.currentLanguage = 0
        self.languageBtn.clicked.connect(self.checkLanguage)
        layout.addWidget(self.languageBtn, alignment=Qt.AlignRight)


        self.instructions_text = QTextEdit(self)
        self.instructions_text.setReadOnly(True)

        # open instruction
        self.changeLanguage(0)
        layout.addWidget(self.instructions_text)
        self.setLayout(layout)

    def checkLanguage(self):
        if self.currentLanguage == 0:
            self.languageBtn.setText("EN")
            self.changeLanguage(1)
            self.currentLanguage = 1

        elif self.currentLanguage == 1:
            self.languageBtn.setText("PL")
            self.changeLanguage(0)
            self.currentLanguage = 0
    def changeLanguage(self, language):

        # standard value = 0
        # 0 = EN
        if language == 0:
            with open("ENinstruction.md", "r", encoding="utf-8") as file:
                content = file.read()
                self.instructions_text.clear()
                self.instructions_text.setMarkdown(content)  # as markdown
        # 1 = PL
        if language == 1:
            with open("PLinstruction.md", "r", encoding="utf-8") as file:
                content = file.read()
                self.instructions_text.clear()
                self.instructions_text.setMarkdown(content)


if __name__ == "__main__":
    app = QApplication([])

    # Set global font
    app.setFont(QFont("Lato", 14))

    startup = POMOKAstartup()
    startup.show()
    app.exec()