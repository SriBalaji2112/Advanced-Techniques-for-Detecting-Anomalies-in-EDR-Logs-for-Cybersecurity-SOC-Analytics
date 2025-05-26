from src.importing import *
from assets.icon import Icon
from src.Files import *

def create_menu(parent):
    menu_bar = QMenuBar(parent)
    icon = Icon()
    # File Menu
    file_menu = menu_bar.addMenu("File")

    open_menu = QAction(icon.open_icon, 'Open file', parent)
    open_menu.setShortcut('Ctrl+O')
    open_menu.triggered.connect(lambda: open_file(parent))
    file_menu.addAction(open_menu)

    save_menu = QAction(icon.save_icon, 'Save file', parent)
    save_menu.setShortcut('Ctrl+S')
    save_menu.triggered.connect(lambda: save_file(parent))
    file_menu.addAction(save_menu)

    export_menu = QMenu("Export", parent)

    # Add actions to the submenu
    pdf_action = QAction("Export as Xlsx", parent)
    export_menu.addAction(pdf_action)

    csv_action = QAction("Export as CSV", parent)
    export_menu.addAction(csv_action)

    file_menu.addMenu(export_menu)

    exit_menu = QAction(icon.exit_icon, 'Exit', parent)
    exit_menu.triggered.connect(parent.close)
    file_menu.addAction(exit_menu)

    # Edit Menu
    edit_menu = menu_bar.addMenu("Edit")
    edit_menu.addAction("Cut")
    edit_menu.addAction("Copy")
    edit_menu.addAction("Paste")

    return menu_bar