# main.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QDesktopWidget, QMessageBox,
                             QAction, QToolBar, QSizePolicy, QSpacerItem)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QSize, QPoint, QTimer, QDateTime

# Importujemy style i klasę bazową okna (zmieniamy import ikon/dźwięków)
from win95_theme import WIN95_QSS, set_win95_font, Win95BaseWindow, get_generated_icon, play_sound, generate_icon_pixmap

# Importujemy aplikacje
from apps.calculator import CalculatorApp
from apps.notepad import NotepadApp
from apps.explorer import ExplorerApp
#from apps.paint import PaintApp # Będzie specjalna integracja z Pygame

class DesktopIcon(QPushButton):
    def __init__(self, name, icon_name, parent=None):
        super().__init__(parent)
        self.name = name
        self.setObjectName("DesktopIcon")
        self.setFixedSize(70, 70)

        # Używamy wygenerowanych ikon
        icon_pixmap = generate_icon_pixmap(icon_name, (200, 200, 200), (0,0,0), "square", 32) # Domyślne kolory
        icon_label = QLabel(self)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.move( (self.width() - icon_pixmap.width()) // 2, 5)

        text_label = QLabel(name, self)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setFont(QFont("MS Sans Serif", 8))
        text_label.setStyleSheet("color: white;")
        text_label.adjustSize()
        text_label.move((self.width() - text_label.width()) // 2, 45)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(icon_label)
        self.layout().addWidget(text_label)
        self.layout().setContentsMargins(0,0,0,0)

        self.selected = False
        self.setCheckable(True)
        self.clicked.connect(self._toggle_selection)


    def _toggle_selection(self):
        self.selected = not self.selected
        if self.selected:
            self.setStyleSheet("QPushButton.DesktopIcon { background-color: rgba(0, 0, 128, 150); border: 1px dotted #DFDFDF; } QLabel { color: white; }")
        else:
            self.setStyleSheet("QPushButton.DesktopIcon { background-color: transparent; border: none; } QLabel { color: white; }")


class DesktopWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows 95")
        self.setObjectName("DesktopWindow")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.open_windows = []
        self.z_order_counter = 0

        self.initUI()
        self.load_desktop_icons()
        play_sound("startup") # Dźwięk startowy

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.desktop_area = QWidget()
        self.desktop_area.setLayout(QVBoxLayout())
        main_layout.addWidget(self.desktop_area)

        taskbar = QWidget()
        taskbar.setObjectName("Taskbar")
        taskbar.setFixedHeight(28)
        taskbar_layout = QHBoxLayout(taskbar)
        taskbar_layout.setContentsMargins(2, 2, 2, 2)
        taskbar_layout.setSpacing(5)

        start_button = QPushButton("Start")
        start_button.setObjectName("StartButton")
        start_button.setIcon(get_generated_icon("start_button", 16)) # Używamy wygenerowanej ikony
        start_button.setFixedSize(70, 22)
        start_button.clicked.connect(self.show_start_menu)
        taskbar_layout.addWidget(start_button)

        self.taskbar_windows_layout = QHBoxLayout()
        self.taskbar_windows_layout.setContentsMargins(0,0,0,0)
        self.taskbar_windows_layout.setSpacing(2)
        taskbar_layout.addLayout(self.taskbar_windows_layout)
        taskbar_layout.addStretch(1)

        self.clock_label = QLabel()
        self.clock_label.setObjectName("ClockLabel")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.update_clock()
        taskbar_layout.addWidget(self.clock_label)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        main_layout.addWidget(taskbar)

    def load_desktop_icons(self):
        icon_spacing_x = 80
        icon_spacing_y = 90
        start_x = 10
        start_y = 10

        my_computer_icon = DesktopIcon("Mój Komputer", "my_computer")
        my_computer_icon.clicked.connect(lambda: self.open_app(ExplorerApp, "Mój Komputer", 600, 400))
        self.desktop_area.layout().addWidget(my_computer_icon)
        my_computer_icon.move(start_x, start_y)

        recycle_bin_icon = DesktopIcon("Kosz", "recycle_bin")
        self.desktop_area.layout().addWidget(recycle_bin_icon)
        recycle_bin_icon.move(start_x, start_y + icon_spacing_y)

        notepad_icon = DesktopIcon("Notatnik", "notepad")
        notepad_icon.clicked.connect(lambda: self.open_app(NotepadApp, "Notatnik", 500, 350))
        self.desktop_area.layout().addWidget(notepad_icon)
        notepad_icon.move(start_x, start_y + 2 * icon_spacing_y)

        calculator_icon = DesktopIcon("Kalkulator", "calculator")
        calculator_icon.clicked.connect(lambda: self.open_app(CalculatorApp, "Kalkulator", 250, 300))
        self.desktop_area.layout().addWidget(calculator_icon)
        calculator_icon.move(start_x, start_y + 3 * icon_spacing_y)

        #paint_icon = DesktopIcon("Paint", "paint")
        #paint_icon.clicked.connect(self.open_paint_app)
        #self.desktop_area.addWidget(paint_icon)
        #paint_icon.move(start_x, start_y + 4 * icon_spacing_y)


    def show_start_menu(self):
        play_sound("click") # Dźwięk kliknięcia
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Start")
        msg_box.setText("Menu Start (w budowie)")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setFont(QFont("MS Sans Serif", 8))
        msg_box.setStyleSheet(WIN95_QSS)
        msg_box.exec_()


    def update_clock(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm AP")
        self.clock_label.setText(current_time)

    def open_app(self, app_class, title, width, height):
        for window in self.open_windows:
            if isinstance(window, app_class):
                window.showNormal()
                window.raise_()
                self.bring_to_front(window)
                return

        app_window = app_class(title=title, width=width, height=height, parent=self.desktop_area)
        app_window.window_manager = self
        app_window.show()

        x_offset = (len(self.open_windows) * 30) % (self.width() - width - 50)
        y_offset = (len(self.open_windows) * 30) % (self.height() - height - 50)
        app_window.move(x_offset + 50, y_offset + 50)

        self.open_windows.append(app_window)
        self.update_taskbar()
        self.bring_to_front(app_window)

    def open_paint_app(self):
        try:
            import subprocess
            # Aby Paint.py działał bez plików ikon/dźwięków, musi być samodzielny
            paint_process = subprocess.Popen([sys.executable, "apps/paint.py"])
            QMessageBox.information(self, "Uwaga", "Paint uruchomiony w osobnym oknie Pygame.\nZamknij je ręcznie.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się uruchomić Paint: {e}")


    def close_app_window(self, window_to_close):
        if window_to_close in self.open_windows:
            self.open_windows.remove(window_to_close)
            window_to_close.close()
            self.update_taskbar()
            self.reorder_windows()

    def update_taskbar(self):
        for i in reversed(range(self.taskbar_windows_layout.count())):
            widget = self.taskbar_windows_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        for window in self.open_windows:
            task_button = QPushButton(window.windowTitle())
            task_button.setFixedSize(120, 22)
            task_button.setCheckable(True)
            task_button.setChecked(window.isVisible() and not window.isMinimized())
            task_button.clicked.connect(lambda checked, w=window: self.toggle_window_state(w, checked))
            self.taskbar_windows_layout.addWidget(task_button)

    def toggle_window_state(self, window, checked):
        play_sound("click") # Dźwięk kliknięcia
        if checked:
            window.showNormal()
            window.raise_()
            self.bring_to_front(window)
        else:
            window.showMinimized()

    def bring_to_front(self, window_to_bring):
        self.z_order_counter += 1
        window_to_bring.stackUnder(self.open_windows[0] if self.open_windows else None)

        if window_to_bring in self.open_windows:
            self.open_windows.remove(window_to_bring)
            self.open_windows.append(window_to_bring)

        for i, window in enumerate(self.open_windows):
            window.stackUnder(self.open_windows[i-1] if i > 0 else None)

    def reorder_windows(self):
        for i, window in enumerate(self.open_windows):
            window.stackUnder(self.open_windows[i-1] if i > 0 else None)


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Zamknij system Windows',
                                     "Czy na pewno chcesz zamknąć system Windows?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            play_sound("shutdown") # Dźwięk zamykania
            QTimer.singleShot(1500, QApplication.quit) # Daj czas na dźwięk
            event.ignore()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    set_win95_font(app)
    app.setStyleSheet(WIN95_QSS)

    desktop = DesktopWindow()
    desktop.show()

    sys.exit(app.exec_())