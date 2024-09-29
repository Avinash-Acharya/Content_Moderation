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

        # navbar
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
       
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.browser.loadProgress.connect(self.update_status)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)

        dark_mode_btn = QAction('Dark Mode', self)
        dark_mode_btn.triggered.connect(self.toggle_dark_mode)
        navbar.addAction(dark_mode_btn)


    def toggle_dark_mode(self):
        if self.browser.page().settings().testAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled):
            self.browser.page().settings().setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, False)
        else:
            self.browser.page().settings().setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
   

    def update_status(self, progress):
        self.status.showMessage(f"Loading... {progress}%")

    def navigate_home(self):
        self.browser.setUrl(QUrl('http://google.com'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())


app = QApplication(sys.argv)
QApplication.setApplicationName('Content Moderation')
window = MainWindow()
app.exec_()