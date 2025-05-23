# apps/explorer.py
from PyQt5.QtWidgets import (QVBoxLayout, QTreeView, QFileSystemModel, QMenuBar, QAction, QWidget,
                             QHBoxLayout, QToolBar, QPushButton, QListView, QLabel, QFrame)
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QDir
from win95_theme import Win95BaseWindow, get_generated_icon # Importujemy klasę bazową i funkcję ikon

class ExplorerApp(Win95BaseWindow):
    def __init__(self, title="Mój Komputer", width=600, height=400, parent=None):
        super().__init__(title, width, height, parent)
        self.init_app_ui()
        self.set_default_view()

    def init_app_ui(self):
        # Pasek Menu
        menu_bar = QMenuBar()
        file_menu = menu_bar.addMenu("&Plik")
        edit_menu = menu_bar.addMenu("&Edycja")
        view_menu = menu_bar.addMenu("&Widok")
        help_menu = menu_bar.addMenu("&Pomoc")

        exit_action = QAction("Wyjdź", self)
        exit_action.triggered.connect(self.close_window_wrapper)
        file_menu.addAction(exit_action)

        self.content_layout.addWidget(menu_bar)

        # Pasek narzędzi
        toolbar = QToolBar()
        from PyQt5.QtCore import QSize
        toolbar.setIconSize(QSize(self.font().pointSize() * 2, self.font().pointSize() * 2)) # Rozmiar ikon na toolbarze
        
        back_action = QAction(get_generated_icon("back_arrow"), "Wstecz", self)
        forward_action = QAction(get_generated_icon("forward_arrow"), "Dalej", self)
        up_action = QAction(get_generated_icon("up_folder"), "W górę", self)
        cut_action = QAction(get_generated_icon("cut"), "Wytnij", self)
        copy_action = QAction(get_generated_icon("copy"), "Kopiuj", self)
        paste_action = QAction(get_generated_icon("paste"), "Wklej", self)
        delete_action = QAction(get_generated_icon("delete"), "Usuń", self)
        properties_action = QAction(get_generated_icon("properties"), "Właściwości", self)
        
        toolbar.addAction(back_action)
        toolbar.addAction(forward_action)
        toolbar.addAction(up_action)
        toolbar.addSeparator()
        toolbar.addAction(cut_action)
        toolbar.addAction(copy_action)
        toolbar.addAction(paste_action)
        toolbar.addSeparator()
        toolbar.addAction(delete_action)
        toolbar.addAction(properties_action)
        
        self.content_layout.addWidget(toolbar)

        # Główny widok (na razie prosta lista)
        self.file_view = QListView()
        self.file_view.setAlternatingRowColors(True) # Fikcyjne, ale estetyczne
        font = self.font()
        font.setPointSize(10)
        self.file_view.setFont(font)
        self.file_view.setStyleSheet("background-color: white; border: none;")
        self.content_layout.addWidget(self.file_view)

        # Model danych dla widoku
        self.model = QStandardItemModel()
        self.file_view.setModel(self.model)

        # Pasek statusu
        self.status_bar.showMessage("Wybierz obiekt, aby wyświetlić właściwości.")

    def set_default_view(self):
        # Symulacja zawartości "Mój Komputer"
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Nazwa', 'Typ', 'Rozmiar']) # Można dodać kolumny w przyszłości

        # Symulowane dyski
        self.add_item("Dysk lokalny (C:)", "folder", "C:", "drive")
        self.add_item("Dysk lokalny (D:)", "folder", "D:", "drive")
        self.add_item("Stacja dyskietek (A:)", "folder", "A:", "floppy")
        self.add_item("Dysk CD-ROM (E:)", "folder", "E:", "cd_rom")

        # Symulowane foldery specjalne
        self.add_item("Panel Sterowania", "folder", "", "control_panel")
        self.add_item("Drukarki", "folder", "", "printers")
        self.add_item("Połączenie sieciowe", "folder", "", "network")


    def add_item(self, name, item_type, size="", icon_path=""):
        item = QStandardItem(name)
        if icon_path:
            # Use generated icon instead of loading from file
            icon = get_generated_icon(icon_path.replace("assets/icons/", "").replace(".png", ""))
            item.setIcon(icon)
        item.setData(item_type, Qt.UserRole + 1)
        item.setData(size, Qt.UserRole + 2)
        self.model.appendRow(item)

    # Można rozbudować o otwarcie folderu, ale to wymagałoby większej logiki symulacji systemu plików.
    # Na razie otwieranie czegokolwiek z Explorera nic nie robi poza wyświetleniem.