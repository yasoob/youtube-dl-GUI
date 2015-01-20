from PyQt4 import QtGui, QtCore
from UI.AboutDialog import Ui_Dialog


class AboutDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
