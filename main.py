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


import threading
import ctypes
import ctypes.wintypes

class DesktopWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows 95")
        self.setObjectName("DesktopWindow")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.open_windows = []
        self.z_order_counter = 0
        self.start_menu_unlocked = False

        self.initUI()
        self.load_desktop_icons()
        play_sound("startup") # Dźwięk startowy

        # Start low-level keyboard hook to block Alt+Tab
        self.hook_thread = threading.Thread(target=self.install_keyboard_hook, daemon=True)
        self.hook_thread.start()

    def install_keyboard_hook(self):
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        WH_KEYBOARD_LL = 13
        WM_KEYDOWN = 0x0100
        WM_SYSKEYDOWN = 0x0104

        alt_pressed = False

        # Define the LowLevelKeyboardProc callback function
        def low_level_keyboard_proc(nCode, wParam, lParam):
            if nCode == 0:
                kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                vk_code = kb_struct.vkCode
                if wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN:
                    # Block Alt+Tab
                    if vk_code == 0x09 and (user32.GetAsyncKeyState(0x12) & 0x8000):
                        return 1  # Block the key event
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        # Define KBDLLHOOKSTRUCT structure
        class KBDLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [
                ("vkCode", ctypes.wintypes.DWORD),
                ("scanCode", ctypes.wintypes.DWORD),
                ("flags", ctypes.wintypes.DWORD),
                ("time", ctypes.wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.wintypes.ULONG)),
            ]

        CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)
        pointer = CMPFUNC(low_level_keyboard_proc)

        hook_id = user32.SetWindowsHookExA(WH_KEYBOARD_LL, pointer, kernel32.GetModuleHandleW(None), 0)
        msg = ctypes.wintypes.MSG()
        while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageA(ctypes.byref(msg))

        user32.UnhookWindowsHookEx(hook_id)

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

        # Internet connectivity icon label
        self.internet_icon_label = QLabel()
        self.internet_icon_label.setObjectName("InternetIconLabel")
        self.internet_icon_label.setFixedSize(32, 20)
        self.internet_icon_label.setAlignment(Qt.AlignCenter)
        taskbar_layout.addWidget(self.internet_icon_label)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        # Timer for internet connectivity check
        self.internet_timer = QTimer(self)
        self.internet_timer.timeout.connect(self.check_internet_connectivity)
        self.internet_timer.start(5000)  # Check every 5 seconds

        main_layout.addWidget(taskbar)
        taskbar_layout.addWidget(self.clock_label)

        # Removed duplicate clock timer setup and update_clock call

        main_layout.addWidget(taskbar)

    def update_clock(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm AP")
        self.clock_label.setText(current_time)

    def check_internet_connectivity(self):
        import socket
        def is_connected():
            try:
                # Connect to Google's DNS server to check internet connectivity
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                return True
            except OSError:
                return False

        connected = is_connected()
        from win95_theme import get_generated_icon
        if connected:
            icon = get_generated_icon("internet_connected", 20)
        else:
            icon = get_generated_icon("internet_disconnected", 20)

        self.internet_icon_label.setPixmap(icon.pixmap(20, 20))

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

        browser_icon = DesktopIcon("Przeglądarka", "network")
        from apps.browser import BrowserApp
        browser_icon.clicked.connect(lambda: self.open_app(BrowserApp, "Przeglądarka", 800, 600))
        self.desktop_area.layout().addWidget(browser_icon)
        browser_icon.move(start_x, start_y + 4 * icon_spacing_y)

        #paint_icon = DesktopIcon("Paint", "paint")
        #paint_icon.clicked.connect(self.open_paint_app)
        #self.desktop_area.addWidget(paint_icon)
        #paint_icon.move(start_x, start_y + 4 * icon_spacing_y)


    def show_start_menu(self):
        if not self.start_menu_unlocked:
            QMessageBox.information(self, "Menu niedostępne", "Menu jest nadal w budowie.")
            return

        play_sound("click")  # Dźwięk kliknięcia
        if hasattr(self, 'start_menu') and self.start_menu.isVisible():
            self.start_menu.hide()
            return

        if not hasattr(self, 'start_menu'):
            self.start_menu = StartMenu(self)
        self.start_menu.adjustSize()
        button = self.findChild(QPushButton, "StartButton")
        pos = button.mapToGlobal(button.rect().bottomLeft())
        pos.setY(pos.y() - self.start_menu.height())
        self.start_menu.move(pos)
        self.start_menu.show()
        self.start_menu.raise_()
        self.start_menu.setFocus()

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

    def unlock_start_menu(self):
        self.start_menu_unlocked = True

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



class StartMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setObjectName("StartMenu")
        self.setStyleSheet(WIN95_QSS)
        self.setFont(QFont("MS Sans Serif", 8))
        self.setFixedWidth(200)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(0)

        # Menu items data: (icon_name, label, submenu)
        menu_items = [
            ("programs", "Programs", ["Program 1", "Program 2", "Program 3"]),
            ("documents", "Documents", ["Document 1", "Document 2"]),
            ("settings", "Settings", ["Control Panel", "Printers"]),
            ("find", "Find", ["Files or Folders", "Computer"]),
            ("help", "Help", ["Windows Help", "About Windows"]),
            (None, "Run...", None),
            (None, "Suspend", None),
            (None, "Shut Down...", None),
        ]

        for icon_name, label, submenu in menu_items:
            item = MenuItem(icon_name, label, submenu, self)
            self.layout.addWidget(item)

        self.layout.addStretch(1)

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)


class MenuItem(QWidget):
    def __init__(self, icon_name, label, submenu, parent=None):
        super().__init__(parent)
        self.setFixedHeight(22)
        self.setObjectName("MenuItem")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 0, 4, 0)
        self.layout.setSpacing(4)

        if icon_name:
            icon_label = QLabel(self)
            icon_icon = get_generated_icon(icon_name, 16)
            icon_pixmap = icon_icon.pixmap(QSize(16, 16))
            icon_label.setPixmap(icon_pixmap)
            icon_label.setFixedSize(16, 16)
            self.layout.addWidget(icon_label)
        else:
            spacer = QSpacerItem(16, 16, QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.layout.addSpacerItem(spacer)

        self.text_label = QLabel(label, self)
        self.text_label.setFont(QFont("MS Sans Serif", 8))
        self.layout.addWidget(self.text_label)

        if submenu:
            arrow_label = QLabel(self)
            arrow_icon = get_generated_icon("submenu_arrow", 8)
            arrow_pixmap = arrow_icon.pixmap(QSize(8, 16))
            arrow_label.setPixmap(arrow_pixmap)
            arrow_label.setFixedSize(8, 16)
            self.layout.addWidget(arrow_label)
            self.submenu = SubMenu(submenu, self)
            self.submenu.hide()
            self.setMouseTracking(True)
            self._hide_timer = None
            self.enterEvent = self.show_submenu
            self.leaveEvent = self.hide_submenu
            self.submenu.installEventFilter(self)
        else:
            self.submenu = None

    def show_submenu(self, event):
        if self.submenu:
            if self._hide_timer:
                self._hide_timer.stop()
                self._hide_timer = None
            pos = self.mapToGlobal(self.rect().topRight())
            self.submenu.move(pos)
            self.submenu.show()

    def hide_submenu(self, event):
        if self.submenu:
            # Delay hiding to allow moving into submenu
            from PyQt5.QtCore import QEvent, QTimer
            def do_hide():
                if not self.submenu.underMouse() and not self.underMouse():
                    self.submenu.hide()
                self._hide_timer = None
            if self._hide_timer:
                self._hide_timer.stop()
            self._hide_timer = QTimer(self)
            self._hide_timer.setSingleShot(True)
            self._hide_timer.timeout.connect(do_hide)
            self._hide_timer.start(300)

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        if obj == self.submenu:
            if event.type() == QEvent.Enter:
                if self._hide_timer:
                    self._hide_timer.stop()
                    self._hide_timer = None
            elif event.type() == QEvent.Leave:
                self.hide_submenu(event)
        return super().eventFilter(obj, event)


class SubMenu(QWidget):
    def __init__(self, items, parent=None):
        super().__init__(parent, Qt.Popup)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setObjectName("SubMenu")
        self.setStyleSheet(WIN95_QSS)
        self.setFont(QFont("MS Sans Serif", 8))
        self.setFixedWidth(180)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(0)

        self.items = []
        for item_text in items:
            item = QLabel(item_text, self)
            item.setFixedHeight(22)
            item.setFont(QFont("MS Sans Serif", 8))
            item.setStyleSheet("padding-left: 4px;")
            item.setMouseTracking(True)
            item.enterEvent = self.item_enter_event
            item.leaveEvent = self.item_leave_event
            self.layout.addWidget(item)
            self.items.append(item)

        self.layout.addStretch(1)

    def item_enter_event(self, event):
        # Keep submenu visible when mouse enters an item
        self.show()
        event.accept()

    def item_leave_event(self, event):
        # Hide submenu if mouse leaves an item and not over submenu or parent MenuItem
        if not self.underMouse() and not self.parent().underMouse():
            self.hide()
        event.accept()

    def closeEvent(self, event):
        # Remove the close event to prevent unexpected app closure
        event.ignore()


if __name__ == '__main__':
    from PyQt5.QtCore import Qt, QCoreApplication
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    set_win95_font(app)
    app.setStyleSheet(WIN95_QSS)

    desktop = DesktopWindow()
    desktop.show()

    sys.exit(app.exec_())
