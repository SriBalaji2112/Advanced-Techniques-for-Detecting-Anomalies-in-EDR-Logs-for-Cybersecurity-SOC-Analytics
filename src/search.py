
from src.importing import *
from widgets.Tables import update_table
from widgets.ContinueProgressBar import ContinousProgressBar
from PyQt5.QtCore import QCoreApplication

def get_table_widget(parent):
    # Retrieve the widget at the given tab index
    current_index = parent.tabs.currentIndex()
    widget = parent.tabs.widget(current_index)
    if isinstance(widget, QTableWidget):
        return widget
    return None

def freeze_search(parent):
    # Perform the search across the entire DataFrame
    progress = ContinousProgressBar("Freezing search results, please wait...", parent=parent)
    progress.show()

    QCoreApplication.processEvents()

    current_index = parent.tabs.currentIndex()
    current_sheet_name = parent.tabs.tabText(current_index)
    search_term = parent.search_input.text()

    QCoreApplication.processEvents()
    new_pivoted_data = {}
    new_pivoted_data[current_sheet_name] = {}
    new_pivoted_data[current_sheet_name]['query'] = parent.data[current_sheet_name]['query']
    QCoreApplication.processEvents()
    new_pivoted_data[current_sheet_name]['df'] = parent.data[current_sheet_name]['df'][parent.data[current_sheet_name]['df'].apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    QCoreApplication.processEvents()
    progress.close()

    update_table(parent, current_index, current_sheet_name, new_pivoted_data[current_sheet_name]['df'])
    parent.data.update(new_pivoted_data.copy())
    # # parent.data[current_sheet_name]['df'] = new_pivoted_data[current_sheet_name]["df"].copy()

def perform_search(parent):
    progress = ContinousProgressBar("Searching data, please wait...", parent=parent)
    progress.show()

    QCoreApplication.processEvents()

    search_text = parent.search_input.text()
    if not search_text:
        return

    # Find all matching cells
    parent.search_results.clear()
    table_widget = get_table_widget(parent)
    for row in range(table_widget.rowCount()):
        for col in range(table_widget.columnCount()):
            item = table_widget.item(row, col)
            if item and search_text.lower() in item.text().lower():
                parent.search_results.append((row, col))

        if row % 20 == 0:
            QCoreApplication.processEvents()

    QCoreApplication.processEvents()
    if parent.search_results:
        parent.current_search_index = 0
        highlight_cell(parent, parent.search_results[parent.current_search_index])
    else:
        QMessageBox.warning(parent, "No Results", "No matching results found.")

    progress.close()

def highlight_cell(parent, cell_position):
    row, col = cell_position
    table_widget = get_table_widget(parent)
    table_widget.setCurrentCell(row, col)

    # Scroll to the selected cell
    table_widget.scrollToItem(table_widget.item(row, col))

    # Resize column to fit the content of the selected cell
    table_widget.resizeColumnToContents(col)

def next_result(parent):
    if parent.search_results:
        parent.current_search_index = (parent.current_search_index + 1) % len(parent.search_results)
        highlight_cell(parent, parent.search_results[parent.current_search_index])

def prev_result(parent):
    if parent.search_results:
        parent.current_search_index = (parent.current_search_index - 1) % len(parent.search_results)
        highlight_cell(parent, parent.search_results[parent.current_search_index])

def clear_search(parent):
    table_widget = get_table_widget(parent)
    parent.search_input.clear()
    parent.search_results.clear()
    parent.current_search_index = -1
    table_widget.clearSelection()