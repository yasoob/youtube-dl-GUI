from PyQt5 import QtCore, QtWidgets
from UI.AboutDialog import Ui_Dialog


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)  # type: ignore
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
