from src.importing import *

from widgets.Menus import create_menu
from widgets.ToolBars import options_toolbar, search_toolbar, filter_options_toolbar
from widgets.Dialogs import show_column_data_dialog, LoadingDialog
from widgets.Tables import display_data
from src.Files import open_file, FileLoaderThread, save_file
from src.pivoting import filter_text_input_on_change

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyrus Log Review Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Data storage
        self.pivoting_count = 0
        self.merge_sheet_count = 0
        self.data = {}
        self.original_data = {}
        self.suggestion_list = []

        # Store search results
        self.search_results = []
        self.current_search_index = -1

        # Central Widget
        central_widget = QWidget()
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        # Adding Components
        self.init_ui()
    
    def init_ui(self):
        # Menu
        self.setMenuBar(create_menu(self))

        # ToolBar
        top_tool_bar_1 = options_toolbar(self)
        top_tool_bar_2 = search_toolbar(self)
        bottom_tool_bar_2 = filter_options_toolbar(self)

        # Add Toolbars
        self.addToolBar(top_tool_bar_1)
        self.addToolBarBreak()
        self.addToolBar(top_tool_bar_2)

        self.addToolBarBreak(Qt.BottomToolBarArea)
        self.addToolBar(Qt.BottomToolBarArea, bottom_tool_bar_2) 

        # Tab Widgets
        # Create a tab widget to hold each sheet's data
        from widgets.Tabs import init_tab, close_tab, on_tab_switched
        self.tabs = init_tab()
        self.tabs.tabCloseRequested.connect(lambda index: close_tab(self, index))
        self.tabs.currentChanged.connect(lambda index: on_tab_switched(self, index))
        self.layout.addWidget(self.tabs)

        # Central Main widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.filter_textbox.textChanged.connect(lambda text: filter_text_input_on_change(self, text))


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()  # Accept the event to close the window
        else:
            event.ignore()  # Ignore the event to keep the window open

    def close_app(self):
        self.close()  # Calls closeEvent() and triggers the window close operation
