from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import *
import sys

class BrowserTab(QWebEngineView):
    """Single browser tab"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUrl(QUrl("https://nytrw.github.io/"))
        self.setFocusPolicy(Qt.StrongFocus)  # Ensure mouse clicks work
        self.setAttribute(Qt.WA_InputMethodEnabled, True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nytrw Browser")
        self.setMinimumSize(1200, 800)

        # ---------------- Tabs ----------------
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.setCentralWidget(self.tabs)

        # ---------------- Toolbar ----------------
        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(28, 28))
        navtb.setStyleSheet("""
            QToolBar { background: #fbe8ff; spacing: 8px; padding: 4px; }
            QToolButton { color: black; font-weight: bold; }
            QToolButton:hover { background: #e0c0ff; border-radius: 5px; }
        """)
        self.addToolBar(navtb)

        # Black icons
        back_btn = QAction(self.style().standardIcon(QStyle.SP_ArrowBack), "", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        navtb.addAction(back_btn)

        forward_btn = QAction(self.style().standardIcon(QStyle.SP_ArrowForward), "", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        navtb.addAction(forward_btn)

        reload_btn = QAction(self.style().standardIcon(QStyle.SP_BrowserReload), "", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        navtb.addAction(reload_btn)

        home_btn = QAction(self.style().standardIcon(QStyle.SP_DirHomeIcon), "", self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        # URL Bar
        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Search Nytrw…")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.urlbar.setStyleSheet("""
            QLineEdit {
                border-radius: 15px;
                padding: 6px 10px;
                background: #fff;
                border: 1px solid #8f34a1;
                color: black;
                selection-background-color: #d4aaff;
            }
        """)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(self.style().standardIcon(QStyle.SP_BrowserStop), "", self)
        stop_btn.triggered.connect(lambda: self.current_browser().stop())
        navtb.addAction(stop_btn)

        new_tab_btn = QAction(self.style().standardIcon(QStyle.SP_FileDialogNewFolder), "", self)
        new_tab_btn.triggered.connect(lambda _: self.add_new_tab())
        navtb.addAction(new_tab_btn)

        # ---------------- Status Bar ----------------
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # ---------------- Tabs signals ----------------
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)

        # Open first tab
        self.add_new_tab(QUrl("https://nytrw.github.io/"), "Nytrw")
        self.show()

    # ---------------- Tabs ----------------
    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl("https://nytrw.github.io/")

        browser = BrowserTab()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda q, b=browser: self.update_urlbar(q, b))
        browser.loadFinished.connect(lambda _, idx=i, b=browser: self.update_tab_title(idx, b))

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def current_tab_changed(self, i):
        browser = self.current_browser()
        if browser is None:
            return
        self.update_urlbar(browser.url(), browser)
        self.update_title(browser)

    def current_browser(self):
        return self.tabs.currentWidget()

    # ---------------- Navigation ----------------
    def navigate_home(self):
        self.current_browser().setUrl(QUrl("https://nytrw.github.io/"))

    def navigate_to_url(self):
        url_text = self.urlbar.text().strip()
        if not url_text:
            return

        # Open full URL if provided
        if url_text.startswith("http://") or url_text.startswith("https://"):
            q = QUrl(url_text)
        else:
            # Otherwise treat it as a Nytrw search
            q = QUrl(f"https://nytrw.github.io/search.html?search={url_text}")

        self.current_browser().setUrl(q)

    # ---------------- UI Updates ----------------
    def update_urlbar(self, q, browser=None):
        if browser != self.current_browser():
            return
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def update_tab_title(self, i, browser):
        title = browser.page().title() or "Nytrw"
        self.tabs.setTabText(i, title)

    def update_title(self, browser):
        page_title = browser.page().title() or ""
        if page_title:
            self.setWindowTitle(f"{page_title} - Nytrw Browser")
        else:
            self.setWindowTitle("Nytrw Browser")


# ---------------- Run Application ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Nytrw Browser")
    window = MainWindow()
    sys.exit(app.exec())
