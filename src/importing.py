from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize, QTimer, QByteArray, QBuffer
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import (
    QApplication,
    QSplashScreen,
    QMainWindow,
    QVBoxLayout,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QProgressDialog,
    QToolBar,
    QAction,
    QTabWidget,
    QLineEdit,
    QPushButton,
    QCompleter,
    QSizePolicy,
    QLabel,
    QDialog,
    QComboBox,
    QDialogButtonBox,
    QHBoxLayout,
    QMessageBox,
    QMenuBar,
    QListWidget,
    QMenu,
)
from PyQt5.QtGui import QColor
import time
import os

pd = None
re = None
sys = None
nx = None
plt = None
FigureCanvas = None

def importing_method(loaded_modules):
    global pd, re, sys, nx, plt, FigureCanvas
    pd = loaded_modules.get("pd")
    re = loaded_modules.get("re")
    sys = loaded_modules.get("sys")
    nx = loaded_modules.get("nx")
    plt = loaded_modules.get("plt")
    FigureCanvas = loaded_modules.get("FigureCanvas")