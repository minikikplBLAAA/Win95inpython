# apps/notepad.py
from PyQt5.QtWidgets import (QVBoxLayout, QTextEdit, QMenuBar, QAction)
from PyQt5.QtCore import Qt
from win95_theme import Win95BaseWindow # Importujemy klasę bazową okna Win95

class NotepadApp(Win95BaseWindow):
    def __init__(self, title="Bez tytułu - Notatnik", width=500, height=350, parent=None):
        super().__init__(title, width, height, parent)
        self.init_app_ui()

    def init_app_ui(self):
        # Menu Notatnika
        menu_bar = QMenuBar()
        file_menu = menu_bar.addMenu("&Plik")
        edit_menu = menu_bar.addMenu("&Edycja")

        # Akcje dla menu Plik
        new_action = QAction("&Nowy", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Otwórz...", self)
        # open_action.triggered.connect(self.open_file) # Na razie nie implementujemy
        file_menu.addAction(open_action)

        save_action = QAction("&Zapisz", self)
        # save_action.triggered.connect(self.save_file) # Na razie nie implementujemy
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Wyjdź", self)
        exit_action.triggered.connect(self.close_window_wrapper) # Wywołaj wrapper, aby zamknąć przez menedżera
        file_menu.addAction(exit_action)

        self.content_editor = QTextEdit()
        font = self.font()
        font.setPointSize(10)
        self.content_editor.setFont(font)
        self.content_editor.setStyleSheet("background-color: white; border: none;") # Notatnik ma białe tło
        self.content_layout.addWidget(self.content_editor)

        # Akcje dla menu Edycja
        undo_action = QAction("&Cofnij", self)
        undo_action.triggered.connect(self.content_editor.undo)
        edit_menu.addAction(undo_action)

        copy_action = QAction("&Kopiuj", self)
        copy_action.triggered.connect(self.content_editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Wklej", self)
        paste_action.triggered.connect(self.content_editor.paste)
        edit_menu.addAction(paste_action)

        cut_action = QAction("&Wytnij", self)
        cut_action.triggered.connect(self.content_editor.cut)
        edit_menu.addAction(cut_action)

        self.content_layout.addWidget(menu_bar)

        # Notatnik nie ma paska stanu
        self.status_bar.setVisible(False)

    def new_file(self):
        self.content_editor.clear()
        self.setWindowTitle("Bez tytułu - Notatnik")
        self.window_title_label.setText(self.windowTitle())