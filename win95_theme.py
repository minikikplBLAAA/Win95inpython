# win95_theme.py
from PyQt5.QtGui import QFont, QIcon, QPixmap, QImage, QPainter, QColor
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QStatusBar
import pygame
import io
from PIL import Image, ImageDraw, ImageFont # Pillow do generowania ikon

# --- Inicjalizacja Pygame do obsługi dźwięków ---
# To musi być zrobione raz na początku działania aplikacji
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
except pygame.error as e:
    print(f"Ostrzeżenie: Nie udało się zainicjalizować pygame.mixer: {e}. Dźwięki będą wyłączone.")
    pygame_mixer_available = False
else:
    pygame_mixer_available = True

# --- Funkcje do generowania prostych dźwięków ---
def generate_beep_sound(frequency=800, duration=0.1):
    if not pygame_mixer_available:
        return None
    sample_rate = pygame.mixer.get_init()[0]
    num_samples = int(sample_rate * duration)
    # Generowanie fali sinusoidalnej
    buffer = bytearray(num_samples * 2) # 2 bytes per sample (16-bit)
    amplitude = 30000  # Max amplitude for 16-bit
    for i in range(num_samples):
        t = float(i) / sample_rate
        sample = int(amplitude * 0.5 * (1.0 + 0.5 * ( (i % 200) / 100 - 1.0)) * (
            0.5 + 0.5 * (i % 1000) / 1000) * (
            0.5 + 0.5 * ((i % 500) / 500) ) ) # Trochę "szumu" jak start Win95
        sample = int(amplitude * 0.5 * (1.0 + 0.5 * ( (i % 200) / 100 - 1.0)) * (
            0.5 + 0.5 * (i % 1000) / 1000) * (
            0.5 + 0.5 * ((i % 500) / 500) ) ) # Trochę "szumu" jak start Win95
        sample = int(amplitude * (
            0.5 * (1.0 + (i % 200) / 100 - 1.0) * (i % 1000) / 1000 +
            0.5 * (i % 500) / 500
        ) * 0.5) # bardziej złożony szum
        sample = max(-32768, min(32767, sample)) # Clamp to 16-bit range
        buffer[2*i:2*i+2] = sample.to_bytes(2, byteorder='little', signed=True)
    return pygame.mixer.Sound(buffer=buffer)

def play_sound(sound_type):
    if not pygame_mixer_available:
        print(f"Dźwięki wyłączone (pygame.mixer niedostępne). Próba odtworzenia: {sound_type}")
        return

    if sound_type == "startup":
        sound = generate_beep_sound(frequency=600, duration=2.5) # Dłuższy, bardziej złożony dźwięk startowy
    elif sound_type == "shutdown":
        sound = generate_beep_sound(frequency=300, duration=1.5) # Krótszy, niższy dźwięk zamknięcia
    elif sound_type == "click":
        sound = generate_beep_sound(frequency=1000, duration=0.05) # Krótki klik
    else:
        return

    if sound:
        try:
            sound.play()
        except pygame.error as e:
            print(f"Błąd odtwarzania dźwięku Pygame: {e}")

# --- Funkcje do generowania ikon za pomocą Pillow ---
def generate_icon_pixmap(text, bg_color, text_color, icon_type="square", size=32):
    # Próbujemy użyć czcionki systemowej, która może być podobna do MS Sans Serif
    try:
        font = ImageFont.truetype("arial.ttf", int(size * 0.6))
    except IOError:
        font = ImageFont.load_default() # Fallback

    img = Image.new('RGBA', (size, size), (0, 0, 0, 0)) # Przezroczyste tło
    draw = ImageDraw.Draw(img)

    # Rysowanie tła (jeśli nie jest przezroczyste)
    if icon_type == "square":
        draw.rectangle((0, 0, size, size), fill=bg_color)
    elif icon_type == "circle":
        draw.ellipse((0, 0, size, size), fill=bg_color)

    # Rysowanie tekstu
    text_bbox = draw.textbbox((0,0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (size - text_width) / 2
    text_y = (size - text_height) / 2 - 2 # Lekka korekta dla centrów

    draw.text((text_x, text_y), text, font=font, fill=text_color)

    # Konwersja PIL Image do QPixmap
    byte_array = io.BytesIO()
    img.save(byte_array, format='PNG')
    byte_array.seek(0)
    q_image = QImage.fromData(byte_array.read())
    return QPixmap.fromImage(q_image)

def get_generated_icon(name, size=32):
    # Możesz tutaj zdefiniować, jakie ikony generować na podstawie nazwy
    if name == "my_computer":
        return QIcon(generate_icon_pixmap("PC", (70, 130, 255), (0,0,0), "square", size))
    elif name == "recycle_bin":
        return QIcon(generate_icon_pixmap("Kos", (220, 220, 220), (0,0,0), "square", size))
    elif name == "notepad":
        return QIcon(generate_icon_pixmap("Txt", (255, 255, 200), (0,0,0), "square", size))
    elif name == "calculator":
        return QIcon(generate_icon_pixmap("123", (180, 255, 180), (0,0,0), "square", size))
    elif name == "paint":
        return QIcon(generate_icon_pixmap("Art", (255, 180, 180), (0,0,0), "square", size))
    elif name == "start_button":
        return QIcon(generate_icon_pixmap(">>", (0, 140, 0), (255,255,255), "square", size)) # Prosta strzałka Start
    elif name == "folder":
        return QIcon(generate_icon_pixmap("F", (255, 220, 0), (0,0,0), "square", size))
    elif name == "file":
        return QIcon(generate_icon_pixmap("[]", (220, 220, 220), (0,0,0), "square", size))
    elif name == "drive":
        return QIcon(generate_icon_pixmap("HDD", (120, 120, 120), (255,255,255), "square", size))
    elif name == "floppy":
        return QIcon(generate_icon_pixmap("A:", (200, 200, 200), (0,0,0), "square", size))
    elif name == "cd_rom":
        return QIcon(generate_icon_pixmap("CD", (120, 120, 255), (0,0,0), "circle", size))
    elif name == "control_panel":
        return QIcon(generate_icon_pixmap("Ctrl", (255, 255, 220), (0,0,0), "square", size))
    elif name == "printers":
        return QIcon(generate_icon_pixmap("Prn", (220, 220, 220), (0,0,0), "square", size))
    elif name == "network":
        return QIcon(generate_icon_pixmap("Net", (180, 255, 180), (0,0,0), "square", size))
    elif name == "back_arrow":
        return QIcon(generate_icon_pixmap("<", (220,220,220), (0,0,0), "square", size))
    elif name == "forward_arrow":
        return QIcon(generate_icon_pixmap(">", (220,220,220), (0,0,0), "square", size))
    elif name == "up_folder":
        return QIcon(generate_icon_pixmap("^", (220,220,220), (0,0,0), "square", size))
    elif name == "cut":
        return QIcon(generate_icon_pixmap("X", (220,220,220), (0,0,0), "square", size))
    elif name == "copy":
        return QIcon(generate_icon_pixmap("C", (220,220,220), (0,0,0), "square", size))
    elif name == "paste":
        return QIcon(generate_icon_pixmap("P", (220,220,220), (0,0,0), "square", size))
    elif name == "delete":
        return QIcon(generate_icon_pixmap("Del", (220,220,220), (0,0,0), "square", size))
    elif name == "properties":
        return QIcon(generate_icon_pixmap("i", (220,220,220), (0,0,0), "square", size))
    else:
        return QIcon(generate_icon_pixmap("?", (255, 0, 0), (255,255,255), "square", size)) # Domyślna ikona błędu

# --- Reszta kodu z win95_theme.py pozostaje bez zmian ---
def set_win95_font(app):
    """Set the application font to MS Sans Serif 8pt to mimic Windows 95 style."""
    font = QFont("MS Sans Serif", 8)
    app.setFont(font)

# (WIN95_QSS, set_win95_font, Win95BaseWindow)
# Pamiętaj, aby zaktualizować import w main.py, aby używał get_generated_icon

# Styl CSS (Qt Style Sheet) dla wyglądu Windows 95
WIN95_QSS = """
    /* Globalne ustawienia dla wszystkich widgetów */
    * {
        font-family: "MS Sans Serif", "Microsoft Sans Serif", "System", "Arial";
        font-size: 8pt;
        color: black;
    }

    /* Główne okno aplikacji (pulpit) */
    #DesktopWindow {
        background-color: #008080; /* Kolor tła pulpitu Win95 (turkusowy) */
    }

    /* Ogólny styl dla ramek okien 3D */
    QFrame[frameShape="1"][frameShadow="2"] { /* Panel, Raised */
        border: 2px outset #FFFFFF;
        border-top-color: #DFDFDF;
        border-left-color: #DFDFDF;
        border-right-color: #808080;
        border-bottom-color: #808080;
        background-color: #C0C0C0; /* Szary Win95 */
    }
    QFrame[frameShape="5"][frameShadow="1"] { /* Panel, Sunken */
        border: 1px inset #FFFFFF;
        border-top-color: #808080;
        border-left-color: #808080;
        border-right-color: #DFDFDF;
        border-bottom-color: #DFDFDF;
        background-color: #C0C0C0; /* Szary Win95 */
    }

    /* Pasek tytułu okien */
    QWidget#title_bar {
        background-color: #000080; /* Ciemnoniebieski Win95 */
        color: white;
        height: 20px; /* Stała wysokość paska tytułu */
    }

    QLabel#window_title_label {
        color: white;
        font-weight: bold;
        padding-left: 2px;
    }

    /* Przyciski na pasku tytułu (minimalizuj, maksymalizuj, zamknij) */
    QPushButton {
        background-color: #C0C0C0;
        border: 2px outset #FFFFFF;
        border-top-color: #DFDFDF;
        border-left-color: #DFDFDF;
        border-right-color: #808080;
        border-bottom-color: #808080;
        font-weight: bold;
        padding: 0px;
    }
    QPushButton:pressed {
        border: 2px inset #FFFFFF;
        border-top-color: #808080;
        border-left-color: #808080;
        border-right-color: #DFDFDF;
        border-bottom-color: #DFDFDF;
        background-color: #DFDFDF;
    }
    QPushButton#close_button {
        background-color: #C0C0C0; /* Na Win95 przycisk X nie był czerwony */
    }
    QPushButton#close_button:hover {
        /* Opcjonalnie: mała zmiana koloru na hover */
        background-color: #DCDCDC;
    }


    /* Pasek Menu */
    QMenuBar {
        background-color: #C0C0C0;
        border-bottom: 1px solid #808080;
        padding: 0px;
        margin: 0px;
    }
    QMenuBar::item {
        padding: 2px 8px;
        background-color: transparent;
    }
    QMenuBar::item:selected {
        background-color: #000080;
        color: white;
    }

    QMenu {
        background-color: #C0C0C0;
        border: 1px outset #FFFFFF;
        border-top-color: #DFDFDF;
        border-left-color: #DFDFDF;
        border-right-color: #808080;
        border-bottom-color: #808080;
        padding: 1px;
    }
    QMenu::item {
        padding: 2px 25px 2px 10px;
        background-color: transparent;
        color: black;
    }
    QMenu::item:selected {
        background-color: #000080;
        color: white;
    }
    QMenu::separator {
        height: 2px;
        background-color: #808080;
        margin-left: 10px;
        margin-right: 10px;
    }

    /* Pasek stanu */
    QStatusBar {
        background-color: #C0C0C0;
        border-top: 1px solid #808080;
        padding: 2px;
        color: black;
    }

    /* Taskbar */
    QWidget#Taskbar {
        background-color: #C0C0C0;
        border-top: 2px outset #FFFFFF;
        border-top-color: #DFDFDF;
        border-bottom-color: #808080; /* Dół taskbara */
    }

    QPushButton#StartButton {
        background-color: #C0C0C0;
        border: 2px outset #FFFFFF;
        border-top-color: #DFDFDF;
        border-left-color: #DFDFDF;
        border-right-color: #808080;
        border-bottom-color: #808080;
        font-weight: bold;
        padding: 2px 5px;
        text-align: left;
    }
    QPushButton#StartButton:pressed {
        border: 2px inset #FFFFFF;
        border-top-color: #808080;
        border-left-color: #808080;
        border-right-color: #DFDFDF;
        border-bottom-color: #DFDFDF;
        background-color: #DFDFDF;
    }

    /* Zegar na pasku zadań */
    QLabel#ClockLabel {
        background-color: #C0C0C0;
        border: 1px inset #FFFFFF;
        border-top-color: #808080;
        border-left-color: #808080;
        border-right-color: #DFDFDF;
        border-bottom-color: #DFDFDF;
        padding: 1px 3px;
        font-size: 7pt; /* Mniejsza czcionka dla zegara */
    }

    /* Ikony na pulpicie */
    QPushButton.DesktopIcon {
        background-color: transparent;
        border: none;
        padding: 5px;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    QPushButton.DesktopIcon:hover {
        background-color: rgba(0, 0, 128, 100); /* Lekko niebieski cień na hover */
        border: 1px dotted #DFDFDF; /* Kropkowana ramka */
    }
    QPushButton.DesktopIcon:selected {
        background-color: rgba(0, 0, 128, 150); /* Ciemniejszy niebieski na selected */
        border: 1px dotted #DFDFDF;
    }
    QPushButton.DesktopIcon QLabel { /* Tekst pod ikoną */
        color: white;
    }

    /* Okna dialogowe / wiadomości */
    QMessageBox {
        background-color: #C0C0C0;
        border: 2px outset #FFFFFF;
        border-top-color: #DFDFDF;
        border-left-color: #DFDFDF;
        border-right-color: #808080;
        border-bottom-color: #808080;
    }
    QMessageBox QPushButton { /* Przyciski w oknach dialogowych */
        min-width: 70px;
        min-height: 20px;
    }
"""

class Win95BaseWindow(QWidget):
    def __init__(self, title="Nowe Okno", width=400, height=300, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height) # Stały rozmiar dla Win95
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window) # Bez ramki, ale jako osobne okno

        self.old_pos = None
        self.dragging = False
        self.is_maximized = False
        self.window_manager = None # Zostanie ustawiony przez DesktopWindow

        self.init_base_ui()

    def init_base_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        outer_frame = QFrame(self)
        outer_frame.setFrameShape(QFrame.Panel)
        outer_frame.setFrameShadow(QFrame.Raised)
        outer_frame.setLineWidth(2)
        outer_frame.setObjectName("outer_frame")

        outer_frame_layout = QVBoxLayout(outer_frame)
        outer_frame_layout.setContentsMargins(0, 0, 0, 0)
        outer_frame_layout.setSpacing(0)

        title_bar = QWidget()
        title_bar.setObjectName("title_bar")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(2, 0, 2, 0)
        title_bar_layout.setSpacing(1)
        title_bar.setFixedHeight(20)

        self.window_title_label = QLabel(self.windowTitle())
        self.window_title_label.setObjectName("window_title_label")
        title_bar_layout.addWidget(self.window_title_label)
        title_bar_layout.addStretch(1)

        self.minimize_button = QPushButton("–")
        self.minimize_button.setFixedSize(20, 18)
        self.minimize_button.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(self.minimize_button)

        self.maximize_button = QPushButton("❐")
        self.maximize_button.setFixedSize(20, 18)
        self.maximize_button.clicked.connect(self.toggleMaximize)
        title_bar_layout.addWidget(self.maximize_button)

        self.close_button = QPushButton("X")
        self.close_button.setObjectName("close_button")
        self.close_button.setFixedSize(20, 18)
        self.close_button.clicked.connect(self.close_window_wrapper)
        title_bar_layout.addWidget(self.close_button)

        outer_frame_layout.addWidget(title_bar)

        self.content_container = QFrame(self)
        self.content_container.setFrameShape(QFrame.Panel)
        self.content_container.setFrameShadow(QFrame.Sunken)
        self.content_container.setLineWidth(1)
        self.content_container.setStyleSheet("background-color: #C0C0C0;")

        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(0)

        outer_frame_layout.addWidget(self.content_container)

        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("MS Sans Serif", 8))
        self.status_bar.showMessage("Gotowy.")
        outer_frame_layout.addWidget(self.status_bar)

        main_layout.addWidget(outer_frame)

        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent
        title_bar.mouseReleaseEvent = self.mouseReleaseEvent

    def close_window_wrapper(self):
        play_sound("click") # Dźwięk kliknięcia przy zamykaniu
        if self.window_manager:
            self.window_manager.close_app_window(self)
        else:
            self.close()

    def mousePressEvent(self, event):
        play_sound("click") # Dźwięk kliknięcia przy naciśnięciu
        if event.button() == Qt.LeftButton:
            if event.y() < self.findChild(QWidget, "title_bar").height():
                self.old_pos = event.globalPos()
                self.dragging = True
            else:
                self.dragging = False
            if self.window_manager:
                self.window_manager.bring_to_front(self)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
            self.dragging = False

    def toggleMaximize(self):
        play_sound("click") # Dźwięk kliknięcia
        if self.is_maximized:
            self.showNormal()
            self.setFixedSize(self.initial_width, self.initial_height)
            self.is_maximized = False
            self.maximize_button.setText("❐")
        else:
            self.initial_width = self.width()
            self.initial_height = self.height()
            self.showMaximized()
            self.setFixedSize(self.screen().size())
            self.is_maximized = True
            self.maximize_button.setText("☐")

    def resizeEvent(self, event):
        self.window_title_label.setText(self.windowTitle())
        super().resizeEvent(event)