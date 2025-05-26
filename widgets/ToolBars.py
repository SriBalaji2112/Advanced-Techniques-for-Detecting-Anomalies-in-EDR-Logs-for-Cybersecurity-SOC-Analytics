from src.importing import *

from assets.icon import Icon
from src.search import perform_search, next_result, prev_result, clear_search, freeze_search
from src.pivoting import save_draft, open_merge_dialog, remove_duplicates, reset_filter, apply_query
from src.Files import save_file, open_file
from widgets.Messages import MessageBox
from views.graph_window import graph_plot
from src.algorithm import start_anomaly_detection

def options_toolbar(parent):
    icon = Icon()
    # Top toolbar
    toolbar = QToolBar("Main Toolbar")

    # Open file action
    parent.open_action = QAction(icon.open_icon, "Open File", parent)
    # parent.open_action.setShortcut("Ctrl+O")
    
    parent.open_action.triggered.connect(lambda: open_file(parent))
    toolbar.addAction(parent.open_action)

    # Save file action
    parent.save_action = QAction(icon.save_icon, "Save File", parent)
    parent.save_action.triggered.connect(lambda: save_file(parent))
    # parent.save_action.setShortcut("Ctrl+S")
    toolbar.addAction(parent.save_action)

    # Separator
    toolbar.addSeparator()

    algorithm_action = QAction(icon.algorithm_icon, "Algorithm", parent)
    algorithm_action.setShortcut("Ctrl+M")
    algorithm_action.triggered.connect(lambda: start_anomaly_detection(parent))
    toolbar.addAction(algorithm_action)

    # Graph button action
    graph_action = QAction(icon.graph_icon, "Graph", parent)
    graph_action.setShortcut("Ctrl+G")
    graph_action.triggered.connect(lambda: graph_plot(parent))
    toolbar.addAction(graph_action)

    # Add a spacer to push the exit button to the right
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    toolbar.addWidget(spacer)

    # Exit action
    exit_action = QAction(icon.exit_icon, "Exit", parent)
    # exit_action.setShortcut("Ctrl+Q")
    exit_action.triggered.connect(parent.close_app)
    toolbar.addAction(exit_action)
    ## Top Tool Bar 1 End
    return toolbar

def search_toolbar(parent):
    icon = Icon()
    # Top Tool Bar 2 Start
    toolbar = QToolBar("Search ToolBar", parent)
    search_text = QLabel("Search : ")
    toolbar.addWidget(search_text)

    parent.search_input = QLineEdit(parent)
    parent.search_input.setPlaceholderText("Search...")

    parent.search_button = QPushButton("Search", parent)
    parent.search_button.setIcon(icon.search_icon)
    parent.search_button.setIconSize(QSize(24, 24))
    parent.search_button.clicked.connect(lambda: perform_search(parent))
    
    parent.freeze_button = QPushButton("Freeze", parent)
    parent.freeze_button.setIcon(icon.tick_icon)
    parent.freeze_button.setIconSize(QSize(24, 24))
    parent.freeze_button.clicked.connect(lambda: freeze_search(parent))
    
    parent.next_button = QPushButton("Next", parent)
    parent.next_button.setIcon(icon.next_icon)
    parent.next_button.setIconSize(QSize(24, 24))
    parent.next_button.clicked.connect(lambda: next_result(parent))

    parent.prev_button = QPushButton("Previous", parent)
    parent.prev_button.setIcon(icon.previous_icon)
    parent.prev_button.setIconSize(QSize(24, 24))
    parent.prev_button.clicked.connect(lambda: prev_result(parent))

    parent.clear_button = QPushButton(parent)
    parent.clear_button.setIcon(icon.search_off_icon)
    parent.clear_button.setIconSize(QSize(24, 24))
    parent.clear_button.clicked.connect(lambda: clear_search(parent))

    toolbar.addWidget(parent.search_input)
    toolbar.addWidget(parent.search_button)
    toolbar.addWidget(parent.freeze_button)
    toolbar.addWidget(parent.prev_button)
    toolbar.addWidget(parent.next_button)
    toolbar.addWidget(parent.clear_button)
    # Top Tool bar End
    
    return toolbar

def filter_options_toolbar(parent):
    # Bottom tool bar 2 Start
    toolbar = QToolBar("Bottom Toolbar")

    # Textbox for filter input
    parent.filter_textbox = QLineEdit(parent)
    parent.filter_textbox.setPlaceholderText("Enter filter condition")
    parent.filter_textbox.setFixedHeight(40)  # Set height of the filter textbox
    toolbar.addWidget(parent.filter_textbox)

    # Apply Filter button
    apply_filter_button = QPushButton("Apply Filter", parent)
    apply_filter_button.setFixedHeight(40)  # Set height of the button
    apply_filter_button.setShortcut("Enter")
    apply_filter_button.clicked.connect(lambda: apply_query(parent))
    toolbar.addWidget(apply_filter_button)

    # Reset Filter button
    save_draft_button = QPushButton("Save Draft", parent)
    save_draft_button.setFixedHeight(40)  # Set height of the button
    save_draft_button.setShortcut("Ctrl+D")
    save_draft_button.clicked.connect(lambda: save_draft(parent))
    toolbar.addWidget(save_draft_button)

    merge_button = QPushButton("Merge Sheets", parent)
    merge_button.setFixedHeight(40)  # Set height of the button
    merge_button.setShortcut("Ctrl+M")
    merge_button.clicked.connect(lambda: open_merge_dialog(parent))
    toolbar.addWidget(merge_button)

    # Remove Duplicates button
    remove_duplicates_button = QPushButton("Remove Duplicates", parent)
    remove_duplicates_button.setFixedHeight(40)  # Set height of the button
    remove_duplicates_button.setShortcut("Ctrl+Shift+R")
    remove_duplicates_button.clicked.connect(lambda: remove_duplicates(parent))
    toolbar.addWidget(remove_duplicates_button)

    # Reset Filter button
    reset_filter_button = QPushButton("Reset Filter", parent)
    reset_filter_button.setFixedHeight(40)  # Set height of the button
    reset_filter_button.setShortcut("Ctrl+Shift+F")
    reset_filter_button.clicked.connect(lambda: reset_filter(parent))
    toolbar.addWidget(reset_filter_button)

    return toolbar