from src.importing import *
import os
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class SplashScreen(QSplashScreen):
    def __init__(self):
        # Initialize splash screen with an image
        # pixmap = QPixmap(400, 300)
        # pixmap.fill(Qt.white)
        pixmap = QPixmap(resource_path("assets\\icons\\splash_screen.jpg"))

        splash_width = 600  # Desired width of the splash screen
        splash_height = 400  # Desired height of the splash screen

        # Scale the image to fit the desired splash screen size, keeping the aspect ratio
        pixmap = pixmap.scaled(splash_width, splash_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        super().__init__(pixmap)
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)


