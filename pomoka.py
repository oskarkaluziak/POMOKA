from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox, QTextEdit
from PySide6.QtGui import QIcon, QPalette, QColor, QFont, QPixmap
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QDesktopServices
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
                font-family: Arial;
            }
        """)

        # Header Container with Stylish Font
        self.header_label = QLabel(self)
        self.header_label.setText("POMOKA")
        self.header_label.setStyleSheet("""
            color: #202124;
            font-size: 48px;
            font-weight: bold;
            font-family: 'Georgia', serif;
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
        self.statBtn = QPushButton("OPEN", self)
        self.statBtn.setCursor(Qt.PointingHandCursor)

        self.modelBtn = QPushButton("MODEL PROGRAM (coming soon)", self)
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
                        border: 2px solid #4285f4;
                        padding: 13px;
                        min-width: 400px;
                        max-width: 400px;
                        height: 25px;
                        border-radius: 8px;
                        font-size: 16px;
                        font-family: 'Georgia', serif;
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

        # Add glowing border effect
        self.addGlowEffect(self.reportBtn)
        self.addGlowEffect(self.instructionsBtn)
        self.addGlowEffect(self.statBtn)

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
            text-align: center;
            margin: 0px 0;
        """)
        layout.addWidget(self.footer_label, alignment=Qt.AlignBottom)
        self.setLayout(layout)

    def addShadowEffect(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 50))
        widget.setGraphicsEffect(shadow)

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

    def addGlowEffect(self, button):
        """Add glowing border effect with a timer for dynamic color changes."""
        self.shadow = QGraphicsDropShadowEffect(button)
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 0)
        button.setGraphicsEffect(self.shadow)

        # Kolory do animacji
        self.colors = [QColor(52, 168, 255)]  # Blue, Red, Green
        self.current_color_index = 0

        # Ustaw timer, aby odświeżać kolor cienia co 500ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateShadowColor)
        self.timer.start(1)

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

class InstructionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instruction")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()
        self.instructions_text = QTextEdit(self)
        self.instructions_text.setReadOnly(True)

        try:
            with open("PLinstruction.md", "r", encoding="utf-8") as file:
                content = file.read()
                self.instructions_text.setMarkdown(content)  # Interpretuj jako Markdown
        except FileNotFoundError:
            self.instructions_text.setPlainText("Instructions file not found.")

        layout.addWidget(self.instructions_text)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])

    # Set global font
    app.setFont(QFont("Arial", 14))

    startup = POMOKAstartup()
    startup.show()
    app.exec()