
from src.importing import *
from widgets.Dialogs import LoadingDialog
from widgets.Tables import display_data
from widgets.Messages import MessageBox
from widgets.ContinueProgressBar import ContinousProgressBar
from PyQt5.QtCore import QCoreApplication

def open_file(parent):
    options = QFileDialog.Options()
    parent.file_path, _ = QFileDialog.getOpenFileName(
        parent, "Open Excel File", "", "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)", options=options
    )

    if parent.file_path:
        parent.loading_dialog = LoadingDialog(parent)
        # error_message = MessageBox()
        parent.loading_dialog.show()
        # parent.loading_dialog = QProgressDialog("Loading...", "Cancel", 0, 100, parent)
        # parent.loading_dialog.setWindowTitle("Please wait for complete process")
        # parent.loading_dialog.setWindowModality(Qt.WindowModal)
        # parent.loading_dialog.setCancelButton(None)
        # parent.loading_dialog.show()

        # Start loading in a separate thread
        parent.loader_thread = FileLoaderThread(parent.file_path)
        parent.loader_thread.data_loaded.connect(lambda data: display_data(parent, data))
        parent.loader_thread.error_occurred.connect(lambda: MessageBox.show_error(parent, "Error", "Sample test Error"))
        parent.loader_thread.progress.connect(parent.loading_dialog.update_progress)
        parent.loader_thread.finished.connect(parent.loading_dialog.hide)
        parent.loader_thread.start()
        # return file_path
        
def save_file(parent):
    # file_path, _ = QFileDialog.getSaveFileName(
    #     parent, "Save File", "", "Excel Files (*.xlsx *.xls);;All Files (*)"
    # )
    # if file_path:
    #     try:
    #         progress = ContinousProgressBar("Saving in progress... Almost there!", parent=parent)
    #         progress.show()

    #         QCoreApplication.processEvents()

    #         with pd.ExcelWriter(file_path) as writer:
    #             for sheet_name, df in parent.data.items():
    #                 df['df'].to_excel(writer, sheet_name=sheet_name, index=False)
    #                 QCoreApplication.processEvents()

    #         progress.close()
    #         # print(f"File saved to {file_path}")
    #     except Exception as e:
    #         print(f"Error saving file: {e}")

    # def save_file(parent):
    file_path, _ = QFileDialog.getSaveFileName(
        parent, "Save File", "", "Excel Files (*.xlsx *.xls);;All Files (*)"
    )

    if file_path:
        progress = ContinousProgressBar("Saving in progress... Almost there!", parent=parent)
        progress.setWindowTitle("Saving File")
        progress.show()

        parent.file_saver = FileSaveWorker(file_path, parent.data)
        parent.file_saver.finished.connect(progress.close)
        parent.file_saver.error.connect(lambda msg: QMessageBox.critical(parent, "Save Error", msg))
        parent.file_saver.start()

class FileSaveWorker(QThread):
    progress_message = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_path, data):
        super().__init__()
        self.file_path = file_path
        self.data = data

    def run(self):
        try:
            with pd.ExcelWriter(self.file_path) as writer:
                for sheet_name, df in self.data.items():
                    df['df'].to_excel(writer, sheet_name=sheet_name, index=False)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class FileLoaderThread(QThread):
    data_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self._is_canceled = False


    def run(self):
        try:
            data = {}  # Dictionary to store sheet names and DataFrames
            file_extension = os.path.splitext(self.file_path)[1].lower()
            self.progress.emit(25)

            if file_extension == '.xlsx':
                excel_file = pd.ExcelFile(self.file_path, engine='openpyxl')  # Use openpyxl for .xlsx
            elif file_extension == '.xls':
                excel_file = pd.ExcelFile(self.file_path, engine='xlrd')  # Use xlrd for .xls
            elif file_extension == '.csv':
                df = pd.read_csv(self.file_path)
                self.progress.emit(50)
                df = df.fillna('')
                self.progress.emit(75)
                data["sheet1"] = {"df": df, "query": ''}
                self.progress.emit(100)
                self.data_loaded.emit(data)
                return
            else:
                raise ValueError("Unsupported file format")

            sheet_names = excel_file.sheet_names
            total_sheets = len(sheet_names)

            for idx, sheet in enumerate(sheet_names):
                if self._is_canceled:
                    return
                df = pd.read_excel(self.file_path, sheet_name=sheet, engine=excel_file.engine)
                df = df.fillna('')
                data[sheet] = {"df": df, "query": ''}
                progress = int(((idx + 1) / total_sheets) * 100)
                self.progress.emit(progress)

            if not self._is_canceled:
                self.data_loaded.emit(data)

        except Exception as e:
            print(e)
            self.error_occurred.emit(str(e))