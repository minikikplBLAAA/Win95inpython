from PyQt5.QtWidgets import (
    QToolBar, QAction, QLineEdit, QStatusBar, QMenuBar, QMenu
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from win95_theme import Win95BaseWindow

class BrowserApp(Win95BaseWindow):
    def __init__(self, title="Internet Explorer", width=900, height=600, parent=None):
        super().__init__(title, width, height, parent)
        self.init_browser_ui()

    def init_browser_ui(self):
        # WebView
        self.webview = QWebEngineView()
        self.webview.setUrl(QUrl("https://google.com"))
        self.content_layout.addWidget(self.webview)

        # Pasek narzędzi
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)

        back_action = QAction("◀", self)
        back_action.triggered.connect(self.webview.back)
        self.toolbar.addAction(back_action)

        forward_action = QAction("▶", self)
        forward_action.triggered.connect(self.webview.forward)
        self.toolbar.addAction(forward_action)

        reload_action = QAction("⟳", self)
        reload_action.triggered.connect(self.webview.reload)
        self.toolbar.addAction(reload_action)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        self.toolbar.addWidget(self.url_bar)

        self.webview.urlChanged.connect(self.update_url)

        self.content_layout.insertWidget(0, self.toolbar)

        # Pasek stanu
        self.status_bar.setVisible(True)
        self.status_bar.showMessage("Gotowy")

        # Menu przeglądarki
        menubar = QMenuBar()
        settings_menu = QMenu("Ustawienia", self)

        retro_action = QAction("Retro User-Agent", self)
        retro_action.triggered.connect(lambda: self.set_user_agent("retro"))
        settings_menu.addAction(retro_action)

        modern_action = QAction("Modern User-Agent", self)
        modern_action.triggered.connect(lambda: self.set_user_agent("modern"))
        settings_menu.addAction(modern_action)

        menubar.addMenu(settings_menu)
        self.content_layout.insertWidget(0, menubar)

        # Domyślnie retro user-agent
        self.set_user_agent("retro")

    def set_user_agent(self, mode):
        page = self.webview.page()
        profile = page.profile()
        if mode == "retro":
            ua = "Mozilla/4.0 (compatible; MSIE 6.0; Windows 95)"
        else:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        profile.setHttpUserAgent(ua)
        self.webview.reload()

    def load_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.webview.setUrl(QUrl(url))

    def update_url(self, qurl):
        self.url_bar.setText(qurl.toString())
