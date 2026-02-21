from PySide6.QtWidgets import QMessageBox

def show_license_error(message: str, title: str = "授权失败") -> None:
    box = QMessageBox()
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle(title)
    box.setText("软件未获得有效授权，无法继续运行。")
    box.setInformativeText(message)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec()
