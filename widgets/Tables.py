from src.importing import *
from widgets.ContinueProgressBar import ContinousProgressBar
from PyQt5.QtCore import QCoreApplication

def create_table(parent, sheet_name, df, progress_lable="Table Rendering, This may take a moment, please wait..."):
    progress = ContinousProgressBar(progress_lable, parent=parent, title="Table Worker")
    progress.show()

    QCoreApplication.processEvents()

    # Create a new widget for this sheet
    tab_exists = False
    for i in range(parent.tabs.count()):
        if parent.tabs.tabText(i) == sheet_name:
            tab_exists = True
            break

    # If the tab does not exist, create a new widget for this sheet
    if not tab_exists:
        parent.table_widget = QTableWidget()
        num_rows = len(df)
        num_columns = len(df.columns)
        
        parent.table_widget.setRowCount(num_rows + 50)  # Add 50 extra rows
        parent.table_widget.setColumnCount(num_columns + 5)  # Add 5 extra columns
        
        parent.table_widget.setHorizontalHeaderLabels(df.columns)
        parent.tabs.addTab(parent.table_widget, sheet_name)
        parent.tabs.setCurrentWidget(parent.table_widget)
        parent.table_widget.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        from functools import partial
        parent.table_widget.horizontalHeader().customContextMenuRequested.connect(partial(on_header_right_click, parent, parent.table_widget))


    # Find the "anomaly" column index
    anomaly_col_index = None  
    if "Anomaly" in df.columns:
        anomaly_col_index = df.columns.get_loc("Anomaly")  # Get index of anomaly column

    for row in range(df.shape[0]):
        is_anomaly = False  # Flag to check if row should be colored

        for col in range(df.shape[1]):
            item = QTableWidgetItem(str(df.iat[row, col]))
            parent.table_widget.setItem(row, col, item)

            # Check if this row has anomaly = -1
            if anomaly_col_index is not None and col == anomaly_col_index and df.iat[row, col] == -1:
                is_anomaly = True  # Mark row for coloring

        # If the row contains an anomaly, set background color for the entire row
        if is_anomaly:
            # print("Anomaly")
            for col in range(df.shape[1]):
                parent.table_widget.item(row, col).setBackground(QColor(245,179,169))  # Set RED color

        if row % 20 == 0:
            QCoreApplication.processEvents()

    progress.close()
# def update_table(parent, index, sheet_name, data_dict):
#     if parent.tabs.tabText(index) == sheet_name:
#         table_widget = parent.tabs.widget(index)
#         parent.filter_textbox.setText(parent.data[sheet_name]['query'])
#         num_rows = len(data_dict)
#         num_columns = len(data_dict.columns)
        
#         # Set a larger number of rows and columns to allow scrolling
#         table_widget.setRowCount(0)  # Add 50 extra rows
#         table_widget.setRowCount(num_rows + 50)  # Add 50 extra rows
#         table_widget.setColumnCount(num_columns + 5)  # Add 5 extra columns
        
#         table_widget.setHorizontalHeaderLabels(data_dict.columns)

#         index = 0
#         # Fill the table with data
#         for row_index, row_data in data_dict.iterrows():
#             for col_index, value in enumerate(row_data):
#                 table_widget.setItem(index, col_index, QTableWidgetItem(str(value)))
#             index += 1

def update_table(parent, index, sheet_name, data_dict, progress_lable="Table Rendering, This may take a moment, please wait..."):
    progress = ContinousProgressBar(progress_lable, parent=parent)
    progress.show()

    QCoreApplication.processEvents()

    if parent.tabs.tabText(index) == sheet_name:
        table_widget = parent.tabs.widget(index)
        parent.filter_textbox.setText(parent.data[sheet_name]['query'])
        num_rows = len(data_dict)
        num_columns = len(data_dict.columns)
        
        table_widget.setRowCount(0)
        table_widget.setRowCount(num_rows + 50)
        table_widget.setColumnCount(num_columns + 5)
        
        table_widget.setHorizontalHeaderLabels(data_dict.columns)

        anomaly_column_index = -1
        if 'Anomaly' in data_dict.columns:
            anomaly_column_index = data_dict.columns.get_loc('Anomaly')

        index = 0
        for row_index, row_data in data_dict.iterrows():
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table_widget.setItem(index, col_index, item)
            
            # Check for -1 in 'Anomaly' column
            if anomaly_column_index != -1 and row_data['Anomaly'] == -1:
                for col_index in range(num_columns):
                    item = table_widget.item(index, col_index)
                    if item:
                        item.setBackground(QColor(255, 200, 200))  # Light red background
            index += 1

            if index % 20 == 0:
                QCoreApplication.processEvents()

    progress.close()
        # from widgets.Dialogs import LoadingDialog
        # from widgets.Messages import MessageBox
        # # loading_dialog = LoadingDialog(parent)
        # # loading_dialog.show()
        # worker = TableDataWorker(data_dict)
        # worker.data_signal.connect(lambda row, col, value: table_widget.setItem(row, col, QTableWidgetItem(value)))
        # # worker.progress_signal.connect(loading_dialog.update_progress)
        # worker.finished_signal.connect(lambda: on_thread_finished(worker))
        # worker.start()
    
class TableDataWorker(QThread):
    progress_signal = pyqtSignal(int)  # Emit progress updates
    data_signal = pyqtSignal(int, int, str)  # Signal to update the table
    finished_signal = pyqtSignal()  # Signal when done

    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df

    def run(self):
        # num_rows = len(self.df)
        index = 0
        # for row_index, row_data in self.df.iterrows():
        #     for col_index, value in enumerate(row_data):
        #         self.data_signal.emit(index, col_index, str(value))
        #     index += 1
        #     progress = int((row_index + 1) / num_rows * 100)
        #     self.progress_signal.emit(progress)
        # self.finished_signal.emit()
        try:
            num_rows = len(self.df)
            for row_index, row_data in self.df.iterrows():
                for col_index, value in enumerate(row_data):
                    if pd.isna(value):
                        value = ''  # Ensure NaN values are replaced with empty strings
                    self.data_signal.emit(index, col_index, str(value))  # Emit data for each cell
                index +=  1
                QThread.msleep(10)
            self.finished_signal.emit()  # Signal that data processing is complete
        except Exception as e:
            self.error_signal.emit(f"Error occurred: {str(e)}")
            self.finished_signal.emit() 


# def create_table(parent, sheet_name, df):
#     # Create a new widget for this sheet
#     tab_exists = False
#     for i in range(parent.tabs.count()):
#         if parent.tabs.tabText(i) == sheet_name:
#             tab_exists = True
#             break

#     # If the tab does not exist, create a new widget for this sheet
#     if not tab_exists:
#         parent.table_widget = QTableWidget()
#         num_rows = len(df)
#         num_columns = len(df.columns)
        
#         parent.table_widget.setRowCount(num_rows + 50)  # Add 50 extra rows
#         parent.table_widget.setColumnCount(num_columns + 5)  # Add 5 extra columns
        
#         parent.table_widget.setHorizontalHeaderLabels(df.columns)
#         parent.tabs.addTab(parent.table_widget, sheet_name)
#         parent.tabs.setCurrentWidget(parent.table_widget)
#         parent.table_widget.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
#         from functools import partial
#         parent.table_widget.horizontalHeader().customContextMenuRequested.connect(partial(on_header_right_click, parent, parent.table_widget))

#         index = 0
#         # Fill the table with data
#         for row_index, row_data in df.iterrows():
#             for col_index, value in enumerate(row_data):
#                 parent.table_widget.setItem(index, col_index, QTableWidgetItem(str(value)))
#             index += 1


#         # from widgets.Dialogs import LoadingDialog
#         # from widgets.Messages import MessageBox
#         # loading_dialog = LoadingDialog(parent)
#         # loading_dialog.show()

#         # worker = TableDataWorker(df)
#         # worker.data_signal.connect(lambda row, col, value: parent.table_widget.setItem(row, col, QTableWidgetItem(value)))
#         # worker.progress_signal.connect(loading_dialog.update_progress)
#         # worker.finished_signal.connect(lambda: on_thread_finished(worker, loading_dialog))
#         # worker.start()


def on_thread_finished(worker, loading_dialog):
    # Hide loading dialog
    loading_dialog.hide()
    # Wait for thread completion
    if worker.isRunning():
        worker.wait()

    worker = None  # Clear reference to worker thread

        
def display_data(parent, data):
    parent.data = data.copy()  # Store loaded data
    parent.original_data = data.copy()

    # Iterate over each sheet in the data dictionary
    for sheet_name, values in data.items():
        # Create a new widget for this sheet
        create_table(parent, sheet_name, values["df"])
        
def on_header_right_click(parent, table_widget, position):
    from widgets.Dialogs import show_column_data_dialog
    header_view = table_widget.horizontalHeader()
    column_index = header_view.logicalIndexAt(position)

    if column_index != -1:  # Ensure a valid column is clicked
        header_name = table_widget.horizontalHeaderItem(column_index).text()

        # Retrieve the column data
        column_data = []
        for row in range(table_widget.rowCount()):
            item = table_widget.item(row, column_index)
            if item is not None:
                if item.text() not in column_data:
                    column_data.append(item.text())
        column_data.sort()
        # Show the dialog with column name and its values
        show_column_data_dialog(parent, header_name, column_data)