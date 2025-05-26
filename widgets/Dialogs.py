from src.importing import *

from widgets.Tables import create_table

text = ""

class MergeDialog(QDialog):
    def __init__(self, sheet_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Sheets")
        self.layout = QVBoxLayout()

        self.sheet_list = QListWidget()
        self.sheet_list.addItems(sheet_names)
        self.sheet_list.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.sheet_list)

        self.file_button = QPushButton("Select Additional Excel Files")
        self.file_button.clicked.connect(self.select_files)
        self.layout.addWidget(self.file_button)

        self.merge_button = QPushButton("Merge Selected Sheets")
        self.merge_button.clicked.connect(self.merge_sheets)
        self.layout.addWidget(self.merge_button)

        self.selected_files = []
        self.setLayout(self.layout)

    def select_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Excel Files", "", "Excel Files (*.xlsx *.xls);;All Files (*)", options=options)
        if files:
            self.selected_files = files

    def merge_sheets(self):
        selected_items = self.sheet_list.selectedItems()
        selected_sheets = [item.text() for item in selected_items]

        if len(selected_sheets) < 2 and not self.selected_files:
            # print("Please select at least two sheets or add files with sheets to merge.")
            return

        merged_data = pd.DataFrame()

        # Merge selected sheets from the current data
        for sheet in selected_sheets:
            if sheet in self.parent().data:
                merged_data = pd.concat([merged_data, self.parent().data[sheet]['df']], ignore_index=True)

        # Merge sheets from the selected files
        for file in self.selected_files:
            additional_data = pd.ExcelFile(file)
            for sheet in additional_data.sheet_names:
                df = additional_data.parse(sheet)
                merged_data = pd.concat([merged_data, df], ignore_index=True)

        # Display the merged data in a new tab
        # self.parent().display_data({"Merged Data": merged_data})
        # # print({"Merged Data": merged_data})
        self.parent().merge_sheet_count += 1
        # self.update_table(current_sheet_name, self.data[current_sheet_name])
        self.parent().data.update({f"Merged Data {self.parent().merge_sheet_count}": {"df": merged_data, "query": ''}})
        self.parent().original_data.update({f"Merged Data {self.parent().merge_sheet_count}": {"df": merged_data, "query": ''}})
        # self.display_data(self.data)
        create_table(self.parent(), f"Merged Data {self.parent().merge_sheet_count}", merged_data)
        
        self.accept()

def show_column_data_dialog(parent, column_name, column_data):
    """
    Show a dialog with the column name and values.
    """
    parent.colum_data_dialog = QDialog(parent)
    parent.colum_data_dialog.setWindowTitle(f"Column: {column_name}")
    
    layout = QVBoxLayout()

    # Add column name label
    column_name_label = QLabel(f"Column Name: {column_name}")
    layout.addWidget(column_name_label)

    # Add a combo box for condition selection (equals, not equals, contains, not contains)
    parent.condition_combo_box = QComboBox()
    parent.condition_combo_box.addItems(["equals", "not equals", "contains", "not contains"])
    parent.condition_combo_box.currentTextChanged.connect(lambda: update_second_input(parent, column_data))
    layout.addWidget(parent.condition_combo_box)

    # Add a placeholder widget for the second option (to be replaced based on condition)
    parent.second_input_container = QVBoxLayout()

    # Initially add the value combo box (will be replaced if necessary)
    parent.value_combo_box = QComboBox()
    parent.value_combo_box.addItems(column_data)  # Add all column values to the combo box
    parent.second_input_container.addWidget(parent.value_combo_box)

    layout.addLayout(parent.second_input_container)

    # Add buttons (OK and Close)
    button_layout = QHBoxLayout()
    ok_button = QDialogButtonBox.Ok
    close_button = QDialogButtonBox.Close
    button_box = QDialogButtonBox(ok_button | close_button)
    
    # Connect the buttons to actions
    button_box.accepted.connect(lambda: on_ok_button_click(parent, column_name))
    button_box.rejected.connect(parent.colum_data_dialog.reject)

    button_layout.addWidget(button_box)
    layout.addLayout(button_layout)

    parent.colum_data_dialog.setLayout(layout)
    parent.colum_data_dialog.show()

def update_second_input(parent, column_data):
    """
    Update the second input field (either combo box or text input)
    based on the selected condition in the first combo box.
    """
    condition = parent.condition_combo_box.currentText()

    # Clear the current layout
    for i in reversed(range(parent.second_input_container.count())):
        widget = parent.second_input_container.itemAt(i).widget()
        if widget is not None:
            widget.deleteLater()

    # Update second input based on the selected condition
    if condition in ["equals", "not equals"]:
        # Show value combo box
        parent.value_combo_box = QComboBox()
        parent.value_combo_box.addItems(column_data)
        parent.second_input_container.addWidget(parent.value_combo_box)
    elif condition in ["contains", "not contains"]:
        # Show text input field
        parent.text_input = QLineEdit()
        parent.text_input.setPlaceholderText("Enter text to match")
        parent.second_input_container.addWidget(parent.text_input)

def on_ok_button_click(parent, colm_name):
    """
    Handle the OK button click, print selected condition and value or text input in the console.
    """
    current_index = parent.tabs.currentIndex()
    current_sheet_name = parent.tabs.tabText(current_index)

    selected_condition = parent.condition_combo_box.currentText()

    text = colm_name + " " + selected_condition + " "

    # Depending on the selected condition, print either the selected value or the entered text
    if selected_condition in ["equals", "not equals"]:
        selected_value = parent.value_combo_box.currentText()
        text += selected_value
    elif selected_condition in ["contains", "not contains"]:
        entered_text = parent.text_input.text()
        text += entered_text
    
    if parent.data[current_sheet_name]['query'] != '':
        parent.data[current_sheet_name]['query'] += " and " + text
    else:
        parent.data[current_sheet_name]['query'] += text

    parent.filter_textbox.setText(parent.data[current_sheet_name]['query'])
    parent.colum_data_dialog.accept()


class LoadingDialog:
    def __init__(self, parent=None, title="File Worker", message="Please wait for the process to complete..."):
        self.dialog = QProgressDialog(message, "Cancel", 0, 100, parent)
        self.dialog.setWindowTitle(title)
        self.dialog.setWindowModality(Qt.WindowModal)
        self.dialog.setCancelButton(None)
        self.dialog.setMaximumWidth(400)
        self.dialog.setMaximumHeight(100)

    def show(self):
        self.dialog.setValue(0)
        self.dialog.show()

    def update_progress(self, value):
        self.dialog.setValue(value)
        if value >= 100:
            self.hide()

    def hide(self):
        self.dialog.hide()