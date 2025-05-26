from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt

class ContinousProgressBar(QProgressDialog):
    def __init__(self, label_text="Processing...", maximum=0, parent=None, title="Worker"):
        super().__init__(label_text, None, 0, maximum, parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumDuration(0)

        self.setMaximumWidth(400)
        self.setMaximumHeight(100)

        # self.setValue(0)
        # self.setAutoClose(False)