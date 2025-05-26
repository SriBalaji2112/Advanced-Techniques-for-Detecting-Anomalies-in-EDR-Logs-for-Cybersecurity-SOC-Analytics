# from src.importing import *

import sys
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMainWindow
import time

loaded_modules = {}
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class LoaderThread(QThread):
    # Signal to notify the main thread when loading is complete
    loading_complete = pyqtSignal()

    def run(self):
        try:
            # Simulate library loading (this can be replaced with real initialization)
            time.sleep(1)  # Simulate delay for splash screen

            # Import libraries
            import pandas as pd
            import re
            import sys
            import networkx as nx
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

            # Simulate additional initialization
            time.sleep(1)
            global loaded_modules
            loaded_modules = {
                "pd": pd,
                "re": re,
                "sys": sys,
                "nx": nx,
                "plt": plt,
                "FigureCanvas": FigureCanvas,
            }
            # Emit the signal to indicate loading is complete
            self.loading_complete.emit()
        except Exception as e:
            print(f"Error during initialization: {e}")

def open_main_window(splash, loader_thread):
    splash.close()  # Close the splash screen
    loader_thread.quit()  # Stop the loader thread
    loader_thread.wait()  # Ensure the thread finishes
    from views.main_window import MainWindow
    main_window = MainWindow()
    main_window.show()

# pyinstaller --name "Cyrus Log Analyzer" --icon assets/icons/logo.ico --onefile --windowed --noconsole --exclude-module PySide6 main.py
if __name__ == "__main__":

    try:
        from assets.icon import Icon
        app = QApplication(sys.argv)

        icon = Icon()
        app.setWindowIcon(icon.app_logo)

        # Show splash screen
        from views.splash_screen import SplashScreen
        splash = SplashScreen()
        splash.show()

        # Start loader thread
        loader_thread = LoaderThread()
        def handle_loading_complete():
            # Close the splash screen and open the main window
            from src.importing import importing_method
            importing_method(loaded_modules)
            open_main_window(splash, loader_thread)

        loader_thread.loading_complete.connect(handle_loading_complete)
        loader_thread.start()

        sys.exit(app.exec_())
    except Exception as E:
        print(E)
