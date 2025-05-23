# apps/calculator.py
from PyQt5.QtWidgets import (QVBoxLayout, QGridLayout, QPushButton, QLineEdit)
from PyQt5.QtCore import Qt
from win95_theme import Win95BaseWindow # Importujemy klasę bazową okna Win95

class CalculatorApp(Win95BaseWindow):
    def __init__(self, title="Kalkulator", width=250, height=300, parent=None):
        super().__init__(title, width, height, parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height) # Kalkulator ma stały rozmiar
        self.expression = ""
        self.init_app_ui()

    def init_app_ui(self):
        # Wyczyść domyślny status bar, jeśli nie jest potrzebny
        self.status_bar.setVisible(False)

        # Pole wyświetlające wynik/wprowadzane cyfry
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        font = self.font()
        font.setPointSize(12)
        self.display.setFont(font) # Większa czcionka dla wyświetlacza
        self.display.setText("0")
        self.display.setStyleSheet("background-color: white; border: 1px inset gray;")
        self.content_layout.addWidget(self.display)

        # Przyciski kalkulatora
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        grid_layout = QGridLayout()
        row = 0
        col = 0
        for button_text in buttons:
            button = QPushButton(button_text)
            button.setFixedSize(50, 40)
            button.clicked.connect(lambda _, text=button_text: self.on_button_click(text))
            grid_layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        # Przycisk C (Clear)
        clear_button = QPushButton("C")
        clear_button.setFixedSize(50, 40)
        clear_button.clicked.connect(self.clear_display)
        grid_layout.addWidget(clear_button, row, col)

        self.content_layout.addLayout(grid_layout)

    def on_button_click(self, text):
        if text == '=':
            try:
                result = str(eval(self.expression))
                self.display.setText(result)
                self.expression = result
            except Exception:
                self.display.setText("Błąd")
                self.expression = ""
        else:
            if self.display.text() == "0" and text != ".":
                self.expression = text
            else:
                self.expression += text
            self.display.setText(self.expression)

    def clear_display(self):
        self.expression = ""
        self.display.setText("0")