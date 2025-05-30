from PyQt5.QtWidgets import (QVBoxLayout, QTextEdit, QMenuBar, QAction)
from PyQt5.QtCore import Qt
from win95_theme import Win95BaseWindow # Importujemy klasę bazową okna Win95
from apps.bsod import BSODScreen

class NotepadApp(Win95BaseWindow):
    def __init__(self, title="Bez tytułu - Notatnik", width=500, height=350, parent=None):
        super().__init__(title, width, height, parent)
        self.menu_unlocked = False
        self.bsod_screen = None
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

        self.content_editor.textChanged.connect(self.check_for_menu_keyword)

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

    def check_for_menu_keyword(self):
        text = self.content_editor.toPlainText().lower()
        if "menu" in text and not self.menu_unlocked:
            if hasattr(self, "window_manager") and self.window_manager:
                self.window_manager.unlock_start_menu()
                self.window_manager.show_start_menu()
                self.menu_unlocked = True
        if "bsod" in text:
            self.show_bsod_screen()

    def show_bsod_screen(self):
        if self.bsod_screen is None:
            self.bsod_screen = BSODScreen()
        self.bsod_screen.show()
        self.bsod_screen.raise_()
        self.bsod_screen.activateWindow()

    # Disabled the real BSOD trigger method for safety
    # def show_bsod(self):
    #     # Trigger a real BSOD on Windows using NtRaiseHardError
    #     # This requires administrative privileges and is dangerous
    #     try:
    #         ctypes.windll.ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(ctypes.c_bool()))
    #         ctypes.windll.ntdll.NtRaiseHardError(0xC0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
    #     except Exception as e:
    #         print(f"Failed to trigger BSOD: {e}")

    def new_file(self):
        self.content_editor.clear()
        self.setWindowTitle("Bez tytułu - Notatnik")
        self.window_title_label.setText(self.windowTitle())
