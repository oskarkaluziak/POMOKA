from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox, QTextEdit
from PySide6.QtGui import QIcon, QFont, QDesktopServices, QGuiApplication
from PySide6.QtCore import Qt, QUrl
from main import POMOKAstat

class POMOKAstartup(QWidget):
    def __init__(self):

        super().__init__()
        self.setupUI()

    def setupUI(self):

        self.setWindowTitle("POMOKA")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.setFixedSize(900, 500)

        self.setStyleSheet("""
                                QWidget {
                                    background-color: #f9fafb;
                                    font-family: 'Roboto';
                                }
                            """)
        self.header_label = QLabel(self)
        self.header_label.setText("POMOKA")
        self.header_label.setStyleSheet("""
                                            color: #202124;
                                            font-size: 48px;
                                            font-weight: bold;
                                            font-family: 'Roboto';
                                            text-align: center;
                                            margin-top: 40px;
                                        """)
        self.header_label.setAlignment(Qt.AlignCenter)

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

        self.statBtn = QPushButton("OPEN", self)
        self.statBtn.setCursor(Qt.PointingHandCursor)

        self.reportBtn = QPushButton("SEND FEEDBACK", self)
        self.reportBtn.setCursor(Qt.PointingHandCursor)

        self.instructionsBtn = QPushButton("INSTRUCTION", self)
        self.instructionsBtn.setCursor(Qt.PointingHandCursor)

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
                                font-family: 'Roboto';
                                font-weight: 460;
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
        self.reportBtn.setStyleSheet(button_style)
        self.instructionsBtn.setStyleSheet(button_style)

        self.statBtn.setToolTip("Launch POMOKA")
        self.reportBtn.setToolTip("Report an issue to administrator")
        self.instructionsBtn.setToolTip("View instruction for using POMOKA")

        self.statBtn.clicked.connect(self.openStatApp)
        self.reportBtn.clicked.connect(self.reportToAdmin)
        self.instructionsBtn.clicked.connect(self.openInstructions)

        layout = QVBoxLayout()
        layout.addWidget(self.header_label, alignment=Qt.AlignTop)
        layout.addWidget(self.subtitle_label, alignment=Qt.AlignTop)
        layout.addStretch()
        layout.addWidget(self.statBtn, alignment=Qt.AlignCenter)
        layout.addWidget(self.instructionsBtn, alignment=Qt.AlignCenter)
        layout.addWidget(self.reportBtn, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.footer_label = QLabel(self)
        self.footer_label.setText("Version 1.0 | © 2025 POMOKA")
        self.footer_label.setStyleSheet("""
                                            color: #5f6368;
                                            font-size: 12px;
                                            font-family: 'Roboto';
                                            text-align: center;
                                            margin: 0px 0;
                                        """)
        layout.addWidget(self.footer_label, alignment=Qt.AlignBottom)
        self.setLayout(layout)
        self.center()

    def center(self):

        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_size = self.geometry()
        window_width = window_size.width()
        window_height = window_size.height()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.setGeometry(x, y, window_width, window_height)

    def openStatApp(self):

        self.StatApp = POMOKAstat()
        self.StatApp.show()

    def updateShadowColor(self):

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
        self.setStyleSheet("""
                                QWidget {
                                    background-color: #f9fafb;
                                    font-family: 'Roboto';
                                    color: #202124;
                                }
                    
                                QTextEdit {
                                    background-color: white;
                                    border: 2px solid #0077B6;
                                    border-radius: 8px;
                                    padding: 10px;
                                    color: #202124;
                                    font-size: 14px;
                                    font-family: 'Roboto';
                                    min-width: 536px;       
                                    max-width: 536px; 
                                    min-height: 300px;      
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
                                font-family: 'Roboto';
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

        layout = QVBoxLayout()
        self.languageBtn = QPushButton("PL", self)
        self.languageBtn.setStyleSheet(button_style)
        self.languageBtn.setToolTip("Change language")
        self.currentLanguage = 0
        self.languageBtn.clicked.connect(self.checkLanguage)
        layout.addWidget(self.languageBtn, alignment=Qt.AlignRight)

        self.instructions_text = QTextEdit(self)
        self.instructions_text.setReadOnly(True)
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

        if language == 0:
            with open("ENinstruction.md", "r", encoding="utf-8") as file:
                content = file.read()
                self.instructions_text.clear()
                self.instructions_text.setMarkdown(content)

        if language == 1:
            with open("PLinstruction.md", "r", encoding="utf-8") as file:
                content = file.read()
                self.instructions_text.clear()
                self.instructions_text.setMarkdown(content)

if __name__ == "__main__":

    app = QApplication([])
    app.setFont(QFont('Roboto', 14))
    startup = POMOKAstartup()
    startup.show()
    app.exec()


print('wprowadz swoje imie')
x = input()
if x < 9:
    x += 1
    print(x)
else:
    print(x)