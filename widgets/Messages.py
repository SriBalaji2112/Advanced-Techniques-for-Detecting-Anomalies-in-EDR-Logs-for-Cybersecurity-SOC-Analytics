from PyQt5.QtWidgets import QMessageBox

class MessageBox:
    @staticmethod
    def show_info(parent, title="Info", message="Nil"):
        QMessageBox.information(parent, title, message)

    @staticmethod
    def show_warning(parent, title="Warning", message="Nil"):
        QMessageBox.warning(parent, title, message)

    @staticmethod
    def show_error(parent, title="Error", message='Nil'):
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def show_question(parent, title="Question", message="Nil"):
        reply = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No
        )
        return reply == QMessageBox.Yes
