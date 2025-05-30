from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class BSODScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #0000AA; color: white;")
        self.setWindowTitle("Blue Screen of Death")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)

        message = QLabel(
            "A problem has been detected and Windows has been shut down to prevent damage\n"
            "to your computer.\n\n"
            "The problem seems to be caused by the following error:\n\n"
            "WIRUS_DETECTED\n\n"
            "If this is the first time you've seen this stop error screen,\n"
            "restart your computer. If this screen appears again, follow\n"
            "these steps:\n\n"
            "Check to make sure any new hardware or software is properly installed.\n"
            "If this is a new installation, ask your hardware or software manufacturer\n"
            "for any Windows updates you might need.\n\n"
            "If problems continue, disable or remove any newly installed hardware\n"
            "or software. Disable BIOS memory options such as caching or shadowing.\n"
            "If you need to use Safe Mode to remove or disable components, restart\n"
            "your computer, press F8 to select Advanced Startup Options, and then\n"
            "select Safe Mode.\n\n"
            "Technical information:\n\n"
            "*** STOP: 0x0000007B (0xFFFFF880009A9928, 0xFFFFFFFFC0000034, 0x0000000000000000, 0x0000000000000000)"
        )
        message.setFont(QFont("MS Sans Serif", 12))
        message.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        message.setWordWrap(True)

        layout.addWidget(message)

    def keyPressEvent(self, event):
        # Allow closing the BSOD screen with Escape key
        if event.key() == Qt.Key_Escape:
            self.close()
