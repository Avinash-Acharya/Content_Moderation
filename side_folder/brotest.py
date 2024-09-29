import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('http://google.com'))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # Navbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        navbar.addWidget(self.progress_bar)
        self.browser.loadProgress.connect(self.update_loading_progress)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.show()  # Ensure the status bar is visible
        self.browser.loadProgress.connect(self.update_status)
        self.browser.loadFinished.connect(self.clear_status)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.tab_widget.addTab(self.browser, "Home")
        new_tab_btn = QAction('New Tab', self)
        new_tab_btn.triggered.connect(self.create_tab)
        navbar.addAction(new_tab_btn)

        self.browser.titleChanged.connect(lambda: self.update_tab_title(self.tab_widget.currentIndex()))

        self.browser.iconChanged.connect(self.update_favicon)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)

        # Dark mode button
        dark_mode_btn = QAction('Dark Mode', self)
        dark_mode_btn.triggered.connect(self.toggle_dark_mode)
        navbar.addAction(dark_mode_btn)

        self.dark_mode_enabled = False

        self.tab_widget.setMovable(True)

        self.setStyleSheet("""
            QMainWindow {
                border-radius: 10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            }
            QToolBar {
                background-color: #f8f8f8;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
            }
        """)

    def toggle_dark_mode(self):
        dark_mode_css = """
        * {
            background-color: #121212 !important;
            color: #ffffff !important;
        }
        a {
            color: #bb86fc !important;
        }
        """
        if not self.dark_mode_enabled:
            self.browser.page().runJavaScript(f"""
            var style = document.createElement('style');
            style.innerHTML = `{dark_mode_css}`;
            document.head.appendChild(style);
            """)
            self.dark_mode_enabled = True
        else:
            self.browser.page().runJavaScript("""
            var styles = document.getElementsByTagName('style');
            if (styles.length > 0) {
                styles[styles.length - 1].remove();
            }
            """)
            self.dark_mode_enabled = False

    def update_loading_progress(self, progress):
        self.progress_bar.setValue(progress)

    def update_favicon(self):
        favicon = self.browser.icon()
        self.url_bar.setStyleSheet(f"border-image: url({favicon}) 0 0 0 0 stretch stretch;")


    def create_tab(self):
        new_browser = QWebEngineView()
        new_browser.setUrl(QUrl("http://google.com"))
        new_tab = QWidget()
        new_tab_layout = QVBoxLayout()
        new_tab_layout.addWidget(new_browser)
        new_tab.setLayout(new_tab_layout)
        self.tab_widget.addTab(new_tab, "New Tab")

    def update_tab_title(self, index):
        tab_title = self.browser.title()
        self.tab_widget.setTabText(index, tab_title)

    def update_status(self, progress):
        self.status.showMessage(f"Loading... {progress}%")

    def clear_status(self):
        self.status.clearMessage()

    def navigate_home(self):
        self.browser.setUrl(QUrl('http://google.com'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())


app = QApplication(sys.argv)
QApplication.setApplicationName('Content Moderation')
window = MainWindow()
app.exec_()
